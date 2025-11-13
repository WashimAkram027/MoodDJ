# MoodDJ AWS Deployment Guide
**Complete Step-by-Step Instructions for Production Deployment**

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Phase 1: Docker Setup](#phase-1-docker-setup)
3. [Phase 2: AWS Account Setup](#phase-2-aws-account-setup)
4. [Phase 3: Terraform Infrastructure](#phase-3-terraform-infrastructure)
5. [Phase 4: CI/CD Pipeline](#phase-4-cicd-pipeline)
6. [Phase 5: Initial Deployment](#phase-5-initial-deployment)
7. [Phase 6: Testing & Verification](#phase-6-testing--verification)
8. [Phase 7: Monitoring Setup](#phase-7-monitoring-setup)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
Install these on your local machine:

```bash
# 1. Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/

# 2. Terraform
# Download from: https://www.terraform.io/downloads
# Or install via chocolatey (Windows):
choco install terraform

# 3. AWS CLI
# Download from: https://aws.amazon.com/cli/
# Or install via chocolatey:
choco install awscli

# 4. Node.js 18+ (already installed)
node --version  # Should be v22.20.0

# 5. Python 3.10+ (already installed)
python --version  # Should be 3.14.0

# 6. Git (already installed)
git --version
```

### AWS Account Setup
1. **Create AWS Account** (if you don't have one)
   - Go to https://aws.amazon.com/
   - Sign up for free tier (12 months free for eligible services)

2. **Create IAM User for Deployment**
   ```
   AWS Console → IAM → Users → Add User

   Username: mooddj-deploy
   Access Type: ✓ Programmatic access

   Permissions: Attach existing policies directly:
   - AmazonEC2ContainerRegistryFullAccess
   - AmazonECS_FullAccess
   - AmazonRDSFullAccess
   - AmazonS3FullAccess
   - CloudFrontFullAccess
   - AmazonRoute53FullAccess
   - SecretsManagerReadWrite
   - CloudWatchFullAccess
   - IAMFullAccess (or PowerUserAccess)
   - ElastiCacheFullAccess

   Save Access Key ID and Secret Access Key!
   ```

3. **Configure AWS CLI**
   ```bash
   aws configure

   # Enter:
   # AWS Access Key ID: <your-access-key>
   # AWS Secret Access Key: <your-secret-key>
   # Default region: us-east-1 (or your preferred region)
   # Default output format: json
   ```

4. **Verify AWS Configuration**
   ```bash
   aws sts get-caller-identity
   # Should show your account details
   ```

### Domain Setup
1. **Purchase/Transfer Domain** (if not already done)
   - Option A: Buy from Route 53 (AWS Console → Route 53 → Register Domain)
   - Option B: Use existing domain (transfer DNS to Route 53)

2. **Create Route 53 Hosted Zone** (if using existing domain)
   ```
   AWS Console → Route 53 → Hosted Zones → Create Hosted Zone

   Domain Name: yourdomain.com
   Type: Public Hosted Zone

   Note the 4 Name Servers (NS records)
   Update these at your domain registrar
   ```

---

## Phase 1: Docker Setup

### Step 1.1: Create Backend Dockerfile

Navigate to backend directory:
```bash
cd C:\Users\akram\MoodDJ\backend
```

Create `Dockerfile`:
```dockerfile
# Multi-stage build for smaller image
FROM python:3.10-slim as builder

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create flask_session directory
RUN mkdir -p flask_session

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Run with gunicorn (production server)
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

Create `.dockerignore`:
```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.env
.env.*
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
*.log
.DS_Store
.spotify_cache
.cache
flask_session/
```

### Step 1.2: Update Backend Requirements

Add Redis support to `requirements.txt`:
```bash
# Append to requirements.txt
redis==5.0.1
flask-session[redis]==0.8.0
gunicorn==21.2.0
eventlet==0.33.3
```

### Step 1.3: Update Backend for Redis Sessions

Edit `backend/app.py`, find the session configuration section and update:
```python
# Session configuration (update this section)
app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE', 'filesystem')  # 'redis' in production
if app.config['SESSION_TYPE'] == 'redis':
    app.config['SESSION_REDIS'] = redis.from_url(os.getenv('SESSION_REDIS'))
else:
    app.config['SESSION_TYPE'] = 'filesystem'

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'mooddj_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
```

Add import at top:
```python
import redis
```

Add health check endpoint in `app.py`:
```python
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

### Step 1.4: Create Frontend Dockerfile

Navigate to frontend directory:
```bash
cd C:\Users\akram\MoodDJ\mooddj-frontend
```

Create `Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # React Router - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Disable logging for favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
}
```

Create `.dockerignore`:
```
node_modules/
build/
.git/
.env
.env.*
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
coverage/
.cache/
```

### Step 1.5: Create Docker Compose (Local Testing)

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mooddj
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backend/database_schema.sql:/docker-entrypoint-initdb.d/schema.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASSWORD=rootpassword
      - DB_NAME=mooddj
      - SESSION_TYPE=redis
      - SESSION_REDIS=redis://redis:6379
      - FLASK_ENV=development
    env_file:
      - ./backend/.env
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./mooddj-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"

volumes:
  mysql_data:
```

### Step 1.6: Test Docker Locally

```bash
# Build and run all services
docker-compose up --build

# Test in browser:
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/api/health

# Stop services
docker-compose down
```

✅ **Phase 1 Complete**: Docker containers working locally

---

## Phase 2: AWS Account Setup

### Step 2.1: Create RDS Database (If Not Already Done)

```bash
# Note: Skip if RDS already exists

# AWS Console → RDS → Create Database
#
# Engine: MySQL 8.0
# Template: Free Tier (or Production for better specs)
# DB Instance Identifier: mooddj-db
# Master Username: admin
# Master Password: <create-strong-password>
#
# VPC: Default (we'll change this with Terraform later)
# Public Access: Yes (for now, will be private later)
# Security Group: Create new "mooddj-db-sg"
#   - Allow 3306 from your IP for setup
#
# Database Name: mooddj
#
# Note the endpoint: mooddj-db.xxxxx.us-east-1.rds.amazonaws.com
```

### Step 2.2: Initialize Database Schema

```bash
# Connect to RDS from local machine
mysql -h <rds-endpoint> -u admin -p

# Run schema (or upload via MySQL Workbench)
source backend/database_schema.sql;

# Verify
USE mooddj;
SHOW TABLES;
# Should see: users, songs, moods, mood_sessions, user_songs

EXIT;
```

### Step 2.3: Store Secrets in AWS Secrets Manager

```bash
# Create secret for database password
aws secretsmanager create-secret \
  --name mooddj/prod/db-password \
  --description "MoodDJ RDS database password" \
  --secret-string "your-rds-password"

# Create secret for Spotify credentials
aws secretsmanager create-secret \
  --name mooddj/prod/spotify-client-secret \
  --secret-string "your-spotify-client-secret"

# Create secret for RapidAPI key
aws secretsmanager create-secret \
  --name mooddj/prod/rapidapi-key \
  --secret-string "your-rapidapi-key"

# Generate and store Flask secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output

aws secretsmanager create-secret \
  --name mooddj/prod/flask-secret-key \
  --secret-string "<paste-generated-key>"

# Verify secrets
aws secretsmanager list-secrets
```

✅ **Phase 2 Complete**: AWS account configured, secrets stored

---

## Phase 3: Terraform Infrastructure

### Step 3.1: Create Terraform Directory Structure

```bash
cd C:\Users\akram\MoodDJ

# Create terraform directory structure
mkdir terraform
cd terraform
mkdir modules
mkdir modules\networking modules\ecs modules\alb modules\s3-cloudfront modules\redis modules\secrets modules\monitoring
mkdir environments
```

### Step 3.2: Create Terraform Backend Configuration

Create `terraform/backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "mooddj-terraform-state"  # Create this bucket manually first
    key            = "mooddj/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "mooddj-terraform-locks"  # Create this table manually first
  }
}
```

**Before running Terraform, create state backend:**
```bash
# Create S3 bucket for state
aws s3 mb s3://mooddj-terraform-state --region us-east-1
aws s3api put-bucket-versioning --bucket mooddj-terraform-state --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket mooddj-terraform-state --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Create DynamoDB table for locks
aws dynamodb create-table \
  --table-name mooddj-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### Step 3.3: Create Root Terraform Files

Create `terraform/variables.tf`:
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "mooddj"
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "rds_endpoint" {
  description = "Existing RDS endpoint"
  type        = string
}

variable "rds_db_name" {
  description = "RDS database name"
  type        = string
  default     = "mooddj"
}

variable "spotify_client_id" {
  description = "Spotify OAuth Client ID"
  type        = string
}

variable "backend_cpu" {
  description = "Backend container CPU units"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Backend container memory (MB)"
  type        = number
  default     = 1024
}
```

Create `terraform/main.tf`:
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}

# Networking Module
module "networking" {
  source = "./modules/networking"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = "10.0.0.0/16"
  azs          = slice(data.aws_availability_zones.available.names, 0, 2)
}

# Secrets Module
module "secrets" {
  source = "./modules/secrets"

  project_name = var.project_name
  environment  = var.environment
}

# Redis Module
module "redis" {
  source = "./modules/redis"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
}

# ECR Repositories
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"

  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  private_subnet_ids  = module.networking.private_subnet_ids
  backend_sg_id       = module.networking.backend_sg_id
  ecr_backend_url     = aws_ecr_repository.backend.repository_url
  backend_cpu         = var.backend_cpu
  backend_memory      = var.backend_memory

  # Environment variables
  rds_endpoint        = var.rds_endpoint
  rds_db_name         = var.rds_db_name
  redis_endpoint      = module.redis.redis_endpoint
  domain_name         = var.domain_name
  spotify_client_id   = var.spotify_client_id

  # Secrets ARNs
  db_password_arn           = module.secrets.db_password_arn
  spotify_client_secret_arn = module.secrets.spotify_client_secret_arn
  rapidapi_key_arn          = module.secrets.rapidapi_key_arn
  flask_secret_key_arn      = module.secrets.flask_secret_key_arn
}

# ALB Module
module "alb" {
  source = "./modules/alb"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  alb_sg_id          = module.networking.alb_sg_id
  backend_target_arn = module.ecs.backend_target_group_arn
  domain_name        = var.domain_name
  certificate_arn    = module.alb.certificate_arn
}

# S3 + CloudFront Module
module "s3_cloudfront" {
  source = "./modules/s3-cloudfront"

  project_name    = var.project_name
  environment     = var.environment
  domain_name     = var.domain_name
  certificate_arn = module.alb.certificate_arn
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  project_name       = var.project_name
  environment        = var.environment
  ecs_cluster_name   = module.ecs.cluster_name
  ecs_service_name   = module.ecs.service_name
  alb_arn_suffix     = module.alb.alb_arn_suffix
  target_group_arn   = module.ecs.backend_target_group_arn
}
```

Create `terraform/outputs.tf`:
```hcl
output "ecr_backend_repository_url" {
  description = "ECR backend repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.s3_cloudfront.cloudfront_domain_name
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = module.s3_cloudfront.s3_bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.s3_cloudfront.cloudfront_distribution_id
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.redis_endpoint
}
```

### Step 3.4: Create Production Variables File

Create `terraform/environments/prod.tfvars`:
```hcl
environment         = "prod"
aws_region         = "us-east-1"
domain_name        = "yourdomain.com"  # REPLACE WITH YOUR DOMAIN
rds_endpoint       = "your-rds-endpoint.region.rds.amazonaws.com"  # REPLACE
spotify_client_id  = "your-spotify-client-id"  # REPLACE
backend_cpu        = 512
backend_memory     = 1024
```

### Step 3.5: Create Terraform Modules

**Due to length, I'll provide the full module code in separate files. Continue to next step.**

---

## Phase 4: Create Terraform Modules

I'll create all the Terraform module files in the next steps. These are lengthy files that define your infrastructure.

---

## Phase 5: CI/CD Pipeline Setup

### Step 5.1: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

```
AWS_ACCESS_KEY_ID = <your-iam-user-access-key>
AWS_SECRET_ACCESS_KEY = <your-iam-user-secret-key>
AWS_REGION = us-east-1
SPOTIFY_CLIENT_ID = <your-spotify-client-id>
```

### Step 5.2: Create GitHub Actions Workflows

Create `.github/workflows/deploy-backend.yml`:
```yaml
name: Deploy Backend

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: mooddj-backend
  ECS_CLUSTER: mooddj-prod-cluster
  ECS_SERVICE: mooddj-prod-backend-service

jobs:
  deploy:
    name: Build and Deploy Backend
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Force ECS service update
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment \
            --region $AWS_REGION

      - name: Wait for deployment to complete
        run: |
          aws ecs wait services-stable \
            --cluster $ECS_CLUSTER \
            --services $ECS_SERVICE \
            --region $AWS_REGION

      - name: Deployment success
        run: echo "Backend deployed successfully!"
```

Create `.github/workflows/deploy-frontend.yml`:
```yaml
name: Deploy Frontend

on:
  push:
    branches:
      - main
    paths:
      - 'mooddj-frontend/**'
      - '.github/workflows/deploy-frontend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}

jobs:
  deploy:
    name: Build and Deploy Frontend
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: mooddj-frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd mooddj-frontend
          npm ci

      - name: Build React app
        env:
          REACT_APP_API_URL: https://api.yourdomain.com
          REACT_APP_WS_URL: https://api.yourdomain.com
        run: |
          cd mooddj-frontend
          npm run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Get S3 bucket name from Terraform output
        id: get-bucket
        run: |
          cd terraform
          terraform init
          BUCKET_NAME=$(terraform output -raw s3_bucket_name)
          echo "bucket_name=$BUCKET_NAME" >> $GITHUB_OUTPUT

      - name: Sync to S3
        run: |
          aws s3 sync mooddj-frontend/build/ s3://${{ steps.get-bucket.outputs.bucket_name }} \
            --delete \
            --cache-control "public, max-age=31536000" \
            --exclude "*.html" \
            --exclude "service-worker.js"

          # HTML files with shorter cache
          aws s3 sync mooddj-frontend/build/ s3://${{ steps.get-bucket.outputs.bucket_name }} \
            --exclude "*" \
            --include "*.html" \
            --include "service-worker.js" \
            --cache-control "public, max-age=0, must-revalidate"

      - name: Get CloudFront distribution ID
        id: get-distribution
        run: |
          cd terraform
          DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
          echo "distribution_id=$DISTRIBUTION_ID" >> $GITHUB_OUTPUT

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ steps.get-distribution.outputs.distribution_id }} \
            --paths "/*"

      - name: Deployment success
        run: echo "Frontend deployed successfully!"
```

---

## Phase 6: Initial Deployment

### Step 6.1: Initialize Terraform

```bash
cd C:\Users\akram\MoodDJ\terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

### Step 6.2: Plan Infrastructure

```bash
# Preview what will be created
terraform plan -var-file=environments/prod.tfvars

# Review output carefully
# Should show:
# - VPC, subnets, security groups
# - ECS cluster, task definitions, services
# - ALB, target groups, listeners
# - ElastiCache Redis
# - S3 bucket, CloudFront distribution
# - CloudWatch log groups
# - IAM roles and policies
```

### Step 6.3: Deploy Infrastructure

```bash
# Apply configuration (this will create all resources)
terraform apply -var-file=environments/prod.tfvars

# Type 'yes' when prompted

# This will take 15-20 minutes
# Wait for completion

# Save outputs
terraform output > ../terraform-outputs.txt
```

### Step 6.4: Build and Push Initial Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Get ECR repository URL from terraform output
ECR_BACKEND=$(terraform output -raw ecr_backend_repository_url)

# Build and push backend
cd ../backend
docker build -t mooddj-backend .
docker tag mooddj-backend:latest $ECR_BACKEND:latest
docker push $ECR_BACKEND:latest

# Force ECS service to deploy
CLUSTER=$(cd ../terraform && terraform output -raw ecs_cluster_name)
SERVICE=$(cd ../terraform && terraform output -raw ecs_service_name)
aws ecs update-service --cluster $CLUSTER --service $SERVICE --force-new-deployment
```

### Step 6.5: Build and Deploy Frontend

```bash
cd ../mooddj-frontend

# Create production .env
cat > .env.production << EOF
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=https://api.yourdomain.com
EOF

# Build
npm run build

# Get S3 bucket name
BUCKET=$(cd ../terraform && terraform output -raw s3_bucket_name)

# Sync to S3
aws s3 sync build/ s3://$BUCKET --delete

# Invalidate CloudFront
DISTRIBUTION=$(cd ../terraform && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION --paths "/*"
```

### Step 6.6: Configure DNS

```bash
# Get ALB DNS name
ALB_DNS=$(cd terraform && terraform output -raw alb_dns_name)
CF_DNS=$(cd terraform && terraform output -raw cloudfront_domain_name)

# In Route 53 Console:
# 1. Go to your hosted zone
# 2. Create A record:
#    Name: api.yourdomain.com
#    Type: A - Alias
#    Alias Target: <ALB_DNS>
#
# 3. Create A record:
#    Name: app.yourdomain.com
#    Type: A - Alias
#    Alias Target: <CF_DNS>
#
# 4. Wait 5-10 minutes for DNS propagation
```

### Step 6.7: Update Spotify Developer Dashboard

1. Go to: https://developer.spotify.com/dashboard
2. Select your MoodDJ app
3. Click "Edit Settings"
4. Add Redirect URI: `https://api.yourdomain.com/api/auth/callback`
5. Save

---

## Phase 7: Testing & Verification

### Step 7.1: Health Checks

```bash
# Test backend health
curl https://api.yourdomain.com/api/health
# Expected: {"status":"healthy"}

# Test frontend
curl -I https://app.yourdomain.com
# Expected: HTTP/2 200
```

### Step 7.2: OAuth Flow Test

1. Open browser: `https://app.yourdomain.com`
2. Click "Connect with Spotify"
3. Authorize on Spotify
4. Should redirect back to dashboard
5. Verify you stay logged in (check session cookie)

### Step 7.3: Mood Detection Test

1. Click "Start Detection" on dashboard
2. Allow camera access
3. Wait for mood detection (every 5 seconds)
4. Verify mood displayed
5. Check browser console for WebSocket messages

### Step 7.4: Music Playback Test

1. Open Spotify app on your device
2. Start playing a song
3. Detect a mood on MoodDJ
4. Verify recommendations appear
5. Click a song to play

### Step 7.5: Load Test (Optional)

```bash
# Install Apache Bench
choco install apache-bench

# Test API endpoint
ab -n 1000 -c 10 https://api.yourdomain.com/api/health

# Review results:
# - Requests per second
# - Mean response time
# - Failed requests (should be 0)
```

---

## Phase 8: Monitoring Setup

### Step 8.1: Create CloudWatch Dashboard

```bash
# AWS Console → CloudWatch → Dashboards → Create Dashboard

# Name: MoodDJ-Production

# Add widgets:
# 1. ECS CPU Utilization (line chart)
# 2. ECS Memory Utilization (line chart)
# 3. ALB Request Count (number)
# 4. ALB Target Response Time (line chart)
# 5. ALB 5XX Errors (number)
# 6. RDS Connections (line chart)
```

### Step 8.2: Configure Alarms

```bash
# Create SNS topic for alerts
aws sns create-topic --name mooddj-alerts

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:mooddj-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription via email

# Alarms are already created by Terraform monitoring module
```

### Step 8.3: View Logs

```bash
# View ECS logs
aws logs tail /ecs/mooddj-prod-backend --follow

# Or in AWS Console → CloudWatch → Log Groups
```

---

## Troubleshooting

### Issue: ECS Task Won't Start

**Symptoms:** ECS service shows 0 running tasks

**Solutions:**
```bash
# Check task events
aws ecs describe-services --cluster CLUSTER_NAME --services SERVICE_NAME

# Check task logs
aws logs tail /ecs/mooddj-prod-backend --since 30m

# Common issues:
# 1. Docker image not found in ECR → Push image again
# 2. Secrets not accessible → Check IAM role permissions
# 3. Health check failing → Check /api/health endpoint
```

### Issue: Frontend Not Loading

**Symptoms:** CloudFront returns 403 or 404

**Solutions:**
```bash
# Check S3 bucket contents
aws s3 ls s3://BUCKET_NAME --recursive

# Verify index.html exists
aws s3 ls s3://BUCKET_NAME/index.html

# Check CloudFront origin settings
aws cloudfront get-distribution --id DISTRIBUTION_ID

# If 404 on routes, verify CloudFront error pages configured
```

### Issue: OAuth Not Working

**Symptoms:** Redirect fails or "invalid callback" error

**Solutions:**
1. Verify Spotify redirect URI matches exactly: `https://api.yourdomain.com/api/auth/callback`
2. Check backend environment variables:
   ```bash
   # Get task definition
   aws ecs describe-task-definition --task-definition mooddj-prod-backend

   # Verify:
   # - SPOTIFY_REDIRECT_URI
   # - FRONTEND_URL
   # - BACKEND_URL
   ```
3. Test redirect manually:
   ```bash
   curl -v https://api.yourdomain.com/api/auth/login
   # Should return auth_url
   ```

### Issue: Session Not Persisting

**Symptoms:** User logged out after refresh

**Solutions:**
1. Check Redis connection:
   ```bash
   # From ECS task
   redis-cli -h REDIS_ENDPOINT ping
   # Should return PONG
   ```
2. Verify sticky sessions enabled on ALB target group
3. Check SESSION_COOKIE_SECURE matches protocol (True for HTTPS)

### Issue: WebSocket Not Connecting

**Symptoms:** Mood detection doesn't update in real-time

**Solutions:**
1. Check browser console for WebSocket errors
2. Verify ALB allows WebSocket upgrade:
   ```bash
   # Check target group attributes
   aws elbv2 describe-target-group-attributes --target-group-arn TG_ARN
   ```
3. Test WebSocket connection:
   ```bash
   # Use wscat tool
   npm install -g wscat
   wscat -c wss://api.yourdomain.com/socket.io/?EIO=4&transport=websocket
   ```

### Issue: High Costs

**Symptoms:** AWS bill higher than expected

**Solutions:**
1. Check CloudWatch costs (can be significant):
   - Reduce log retention (default 7 days is enough)
   - Delete unused log groups
2. Check NAT Gateway costs ($0.045/hour):
   - Consider removing NAT for cost savings (ECS pulls images via VPC endpoint)
3. Check RDS instance size:
   - Downgrade to db.t3.micro if on free tier
4. Enable S3 lifecycle policies:
   - Delete old CloudFront logs after 30 days

---

## Maintenance Commands

### Update Backend Code

```bash
# Push code to main branch
git add backend/
git commit -m "Update backend"
git push origin main

# GitHub Actions automatically:
# 1. Builds Docker image
# 2. Pushes to ECR
# 3. Updates ECS service
```

### Update Frontend Code

```bash
# Push code to main branch
git add mooddj-frontend/
git commit -m "Update frontend"
git push origin main

# GitHub Actions automatically:
# 1. Builds React app
# 2. Syncs to S3
# 3. Invalidates CloudFront
```

### Manual ECS Rollback

```bash
# List task definition revisions
aws ecs list-task-definitions --family-prefix mooddj-prod-backend

# Update service to previous revision
aws ecs update-service \
  --cluster mooddj-prod-cluster \
  --service mooddj-prod-backend-service \
  --task-definition mooddj-prod-backend:PREVIOUS_REVISION
```

### Scale ECS Service

```bash
# Scale up
aws ecs update-service \
  --cluster mooddj-prod-cluster \
  --service mooddj-prod-backend-service \
  --desired-count 2

# Scale down
aws ecs update-service \
  --cluster mooddj-prod-cluster \
  --service mooddj-prod-backend-service \
  --desired-count 1
```

### Destroy Infrastructure (Cleanup)

```bash
# DANGER: This will delete ALL resources
cd terraform
terraform destroy -var-file=environments/prod.tfvars

# Type 'yes' to confirm

# Manually delete:
# - S3 buckets (if not empty)
# - ECR images
# - CloudWatch logs (optional)
```

---

## Cost Breakdown

**Monthly Costs (Small Traffic < 100 Users):**

| Service | Cost | Notes |
|---------|------|-------|
| ECS Fargate | $15-25 | 0.5 vCPU, 1GB RAM, 1 task, ~730 hrs/month |
| ElastiCache Redis | $13 | cache.t3.micro, 1 node |
| RDS MySQL | $15-20 | db.t3.micro (or free tier) |
| Application Load Balancer | $16 | Fixed monthly cost |
| S3 Storage | $0.50 | ~5GB frontend files |
| CloudFront | $1-5 | First 1TB free, then $0.085/GB |
| Route 53 | $0.50 | 1 hosted zone |
| Secrets Manager | $1.60 | 4 secrets × $0.40 |
| Data Transfer | $5-10 | Outbound to internet |
| **Total** | **$68-91** | Can optimize to ~$50 |

**Cost Optimization Tips:**
- Use RDS free tier (750 hrs/month for 12 months)
- Delete unused CloudWatch logs
- Use S3 Intelligent-Tiering
- Enable CloudFront caching (reduce origin requests)
- Schedule ECS tasks (stop during off-hours if testing)

---

## Next Steps After Deployment

1. **Request Spotify Extended Quota** (for unlimited users)
   - Go to Spotify Developer Dashboard
   - Request quota extension (takes 5-7 days)

2. **Add Custom Domain to Spotify** (if you have a brand)
   - Update app name, description, logo
   - Add privacy policy URL

3. **Implement Analytics**
   - Add Google Analytics to frontend
   - Track user sessions, mood detection events

4. **Set Up Backups**
   - Enable RDS automated backups (7-day retention)
   - Export Terraform state periodically
   - Document disaster recovery plan

5. **Add Tests** (for future CI/CD enhancement)
   - Backend: Pytest for API endpoints
   - Frontend: Jest + React Testing Library

6. **Performance Optimization**
   - Enable gzip compression (already in nginx.conf)
   - Optimize images (use WebP format)
   - Lazy load React components
   - Add Redis caching for frequent DB queries

7. **Security Hardening**
   - Enable AWS WAF (Web Application Firewall)
   - Add rate limiting to API endpoints
   - Implement IP whitelisting for admin routes
   - Enable MFA for AWS root account

---

## Support & Resources

**AWS Documentation:**
- ECS: https://docs.aws.amazon.com/ecs/
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

**Community:**
- Terraform: https://discuss.hashicorp.com/
- AWS: https://repost.aws/

**Your Project:**
- GitHub Repo: https://github.com/WashimAkram027/MoodDJ
- Spotify Dashboard: https://developer.spotify.com/dashboard

---

**Congratulations!** You now have a production-ready, cloud-native application with Infrastructure as Code and CI/CD automation. This deployment showcases skills highly valued in DevOps and Cloud Engineering roles.
