# MoodDJ EC2 Deployment Guide
**Simple Containerized Deployment with Docker Compose**

---

## Table of Contents
1. [Current Deployment Status](#current-deployment-status)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Local Testing](#local-testing)
5. [EC2 Deployment Setup](#ec2-deployment-setup)
6. [Initial Deployment](#initial-deployment)
7. [Domain Configuration](#domain-configuration)
8. [Updating the Application](#updating-the-application)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)
11. [Cost Breakdown](#cost-breakdown)

---

## Current Deployment Status

✅ **Live Website:** Deployed on AWS EC2
✅ **Infrastructure:** Single EC2 instance (t2.small/t2.medium)
✅ **Container Orchestration:** Docker Compose
✅ **Database:** AWS RDS MySQL (ca-central-1)
✅ **Domain:** GoDaddy domain pointing to EC2 public IP
✅ **Deployment Method:** Manual via SSH with automated scripts

**Why This Approach:**
After evaluating complex solutions (Terraform + ECS, AWS Copilot), we chose EC2 with Docker Compose for:
- Simplicity and quick iteration
- Lower cost ($15-30/month vs $60-90/month)
- Easy debugging and direct access
- Sufficient for MVP and small-to-medium traffic
- Can migrate to ECS/Kubernetes later if needed

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   GoDaddy Domain                     │
│              (DNS A Record → EC2 IP)                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              AWS EC2 Instance                        │
│           (t2.small/medium, Ubuntu)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │         Docker Compose Services              │  │
│  │                                              │  │
│  │  ┌──────────────┐  ┌────────────────────┐  │  │
│  │  │   Frontend   │  │      Backend       │  │  │
│  │  │  (Nginx:80)  │  │   (Flask:5000)     │  │  │
│  │  │ React Build  │  │  Python + OpenCV   │  │  │
│  │  └──────┬───────┘  └──────┬─────────────┘  │  │
│  │         │                  │                 │  │
│  │         └──────────┬───────┘                 │  │
│  │                    │                         │  │
│  │         ┌──────────▼──────────┐             │  │
│  │         │   Local MySQL       │             │  │
│  │         │  (Port 3306)        │             │  │
│  │         │  (For local dev)    │             │  │
│  │         └─────────────────────┘             │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  Ports Exposed:                                     │
│  - 80 (Frontend)                                   │
│  - 5000 (Backend API)                              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            AWS RDS MySQL Database                   │
│        (mooddj-database.c9wc8gkmgine...)           │
│                (ca-central-1)                       │
└─────────────────────────────────────────────────────┘
```

---

## Prerequisites

### On Your Local Machine:
1. **Git** - Already installed ✓
2. **Docker Desktop** - For local testing
   ```bash
   # Download from: https://www.docker.com/products/docker-desktop/
   ```
3. **AWS CLI** - For managing EC2
   ```bash
   # Download from: https://aws.amazon.com/cli/
   aws --version
   ```
4. **SSH Client** - For connecting to EC2 (built-in on Windows/Mac/Linux)

### AWS Account:
1. **EC2 Instance** - t2.small or t2.medium with Ubuntu
2. **RDS MySQL** - Already configured ✓
3. **Security Groups** - Properly configured
4. **Key Pair** - `mooddj-key.pem` ✓

### Domain:
1. **GoDaddy Domain** - Already purchased ✓
2. **DNS Configuration** - A record pointing to EC2 IP ✓

---

## Local Testing

Before deploying to EC2, test everything locally using Docker Compose.

### Step 1: Update Environment Variables

**Backend (`backend/.env`):**
```env
# AWS RDS Database Configuration
DB_HOST=mooddj-database.c9wc8gkmgine.ca-central-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=Tensorflow_python786
DB_NAME=mooddj
DB_PORT=3306

# Flask Configuration
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=development

# Spotify API Credentials
SPOTIFY_CLIENT_ID=987339e67f5a49bf8225ca6c944f41ca
SPOTIFY_CLIENT_SECRET=913856a259f84195b6d769288f481f4a
SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/api/auth/callback

# RapidAPI Configuration
RAPIDAPI_KEY=a07bdb5faemsh4e902b0093f5565p1f95b8jsndba5b9cbb3c8
RAPIDAPI_HOST=track-analysis.p.rapidapi.com
```

**Frontend (`mooddj-frontend/.env`):**
```env
REACT_APP_API_URL=http://127.0.0.1:5000
REACT_APP_WS_URL=http://127.0.0.1:5000
```

### Step 2: Build and Run with Docker Compose

```bash
# From project root
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Step 3: Test Locally

1. **Frontend:** http://127.0.0.1:3000
2. **Backend API:** http://127.0.0.1:5000/api/health
3. **Test OAuth:** Click "Connect with Spotify"
4. **Test Mood Detection:** Allow camera access and start detection

### Step 4: Stop Services

```bash
docker-compose down
```

---

## EC2 Deployment Setup

### Step 1: Launch EC2 Instance (If Not Already Done)

**Instance Configuration:**
- **AMI:** Ubuntu Server 22.04 LTS
- **Instance Type:** t2.small or t2.medium
- **Storage:** 20-30 GB gp3
- **Key Pair:** mooddj-key.pem
- **Security Group:** See configuration below

**Security Group Rules:**

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| SSH | TCP | 22 | Your IP | Remote access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Frontend access |
| HTTPS | TCP | 443 | 0.0.0.0/0 | SSL (future) |
| Custom TCP | TCP | 5000 | 0.0.0.0/0 | Backend API |
| Custom TCP | TCP | 3000 | Your IP | Development testing |
| MySQL/Aurora | TCP | 3306 | EC2 Security Group | RDS access |

### Step 2: Connect to EC2 Instance

```bash
# From your local machine
chmod 400 mooddj-key.pem
ssh -i mooddj-key.pem ubuntu@<EC2_PUBLIC_IP>
```

**Replace `<EC2_PUBLIC_IP>` with your instance's public IP address**

### Step 3: Install Docker on EC2

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt-get install -y docker-compose

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
```

**Reconnect to EC2:**
```bash
ssh -i mooddj-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### Step 4: Install Git and Clone Repository

```bash
# Install git
sudo apt-get install -y git

# Clone your repository
git clone https://github.com/WashimAkram027/MoodDJ.git
cd MoodDJ
```

---

## Initial Deployment

### Step 1: Configure Environment Variables for Production

**Update Backend `.env`:**
```bash
cd ~/MoodDJ/backend
nano .env
```

Update these values:
```env
# Keep database settings as-is (RDS)
DB_HOST=mooddj-database.c9wc8gkmgine.ca-central-1.rds.amazonaws.com

# Update Spotify redirect URI to your domain or EC2 IP
SPOTIFY_REDIRECT_URI=http://<YOUR_DOMAIN_OR_IP>:5000/api/auth/callback

# Update frontend/backend URLs
FRONTEND_URL=http://<YOUR_DOMAIN_OR_IP>
BACKEND_URL=http://<YOUR_DOMAIN_OR_IP>:5000

# For production, consider using Redis sessions (optional)
SESSION_TYPE=filesystem
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_SAMESITE=Lax

# Set strong secret key
SECRET_KEY=<generate-random-secret-key>
FLASK_ENV=production
```

**Generate a secret key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Update Frontend `.env`:**
```bash
cd ~/MoodDJ/mooddj-frontend
nano .env
```

```env
REACT_APP_API_URL=http://<YOUR_DOMAIN_OR_IP>:5000
REACT_APP_WS_URL=http://<YOUR_DOMAIN_OR_IP>:5000
```

### Step 2: Update Docker Compose for Production

**Edit `docker-compose.yml`:**
```bash
cd ~/MoodDJ
nano docker-compose.yml
```

The existing configuration should work, but verify:
- Backend connects to AWS RDS (not local MySQL)
- Ports are correctly mapped
- Environment variables are properly set

### Step 3: Build Frontend for Production

```bash
cd ~/MoodDJ/mooddj-frontend
nano .env.production
```

Add:
```env
REACT_APP_API_URL=http://<YOUR_DOMAIN_OR_IP>:5000
REACT_APP_WS_URL=http://<YOUR_DOMAIN_OR_IP>:5000
```

### Step 4: Update Spotify Developer Dashboard

1. Go to https://developer.spotify.com/dashboard
2. Select your MoodDJ app
3. Click "Edit Settings"
4. Add Redirect URI: `http://<YOUR_DOMAIN_OR_IP>:5000/api/auth/callback`
5. Save

### Step 5: Deploy with Docker Compose

```bash
cd ~/MoodDJ

# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Verify services are running:**
```bash
# Check backend health
curl http://localhost:5000/api/health

# Check frontend
curl http://localhost:80
```

### Step 6: Configure Firewall (Optional but Recommended)

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH, HTTP, Backend API
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

---

## Domain Configuration

### Option 1: Using GoDaddy Domain (Current Setup)

1. **Get EC2 Public IP:**
   ```bash
   curl http://checkip.amazonaws.com
   ```

2. **Configure DNS in GoDaddy:**
   - Log in to GoDaddy account
   - Go to DNS Management for your domain
   - Add/Update A Record:
     - **Type:** A
     - **Name:** @ (for root domain) or www
     - **Value:** <EC2_PUBLIC_IP>
     - **TTL:** 600 (10 minutes)
   - Save changes

3. **Wait for DNS Propagation** (5-30 minutes)
   ```bash
   # Check DNS propagation
   nslookup yourdomain.com
   ```

4. **Update Environment Variables** with your domain

### Option 2: Using EC2 Public IP Directly

If not using a domain, access via:
- Frontend: `http://<EC2_PUBLIC_IP>`
- Backend: `http://<EC2_PUBLIC_IP>:5000`

**Note:** EC2 public IPs change on restart. Consider using Elastic IP for persistence.

### Option 3: Elastic IP (Recommended for Production)

```bash
# Allocate Elastic IP via AWS Console or CLI
aws ec2 allocate-address --domain vpc

# Associate with your EC2 instance
aws ec2 associate-address --instance-id <INSTANCE_ID> --public-ip <ELASTIC_IP>
```

---

## Updating the Application

### Method 1: Manual Update via SSH

```bash
# SSH into EC2
ssh -i mooddj-key.pem ubuntu@<EC2_IP>

# Navigate to project
cd ~/MoodDJ

# Pull latest changes
git pull origin washimbranch  # or main

# Rebuild and restart services
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Method 2: Quick Backend Update (Without Downtime)

```bash
# Pull changes
cd ~/MoodDJ
git pull

# Rebuild only backend
docker-compose up -d --build backend

# Check if backend restarted successfully
docker-compose logs backend
```

### Method 3: Frontend-Only Update

```bash
# Pull changes
cd ~/MoodDJ
git pull

# Rebuild only frontend
docker-compose up -d --build frontend
```

### Automated Deployment Script (Optional)

Create `deploy.sh` on EC2:
```bash
#!/bin/bash
cd ~/MoodDJ
git pull origin washimbranch
docker-compose down
docker-compose up -d --build
echo "Deployment complete!"
docker-compose ps
```

Make executable:
```bash
chmod +x deploy.sh
```

Run with:
```bash
./deploy.sh
```

---

## Monitoring & Maintenance

### Check Application Status

```bash
# Check running containers
docker-compose ps

# Check container resource usage
docker stats

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check last 100 lines
docker-compose logs --tail=100 backend
```

### Database Connection Test

```bash
# Test RDS connection from EC2
mysql -h mooddj-database.c9wc8gkmgine.ca-central-1.rds.amazonaws.com -u admin -p

# Once connected:
USE mooddj;
SHOW TABLES;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM songs;
EXIT;
```

### Disk Space Management

```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up unused Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Auto-Restart on EC2 Reboot

```bash
# Create systemd service for docker-compose
sudo nano /etc/systemd/system/mooddj.service
```

Add:
```ini
[Unit]
Description=MoodDJ Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/MoodDJ
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable mooddj.service
sudo systemctl start mooddj.service
```

### Backup Strategy

**Database Backups (RDS):**
- AWS RDS automatic backups are enabled by default
- Retention period: 7 days
- Manual snapshots: Create via AWS Console when needed

**Application Code Backups:**
- Code is backed up in GitHub repository
- Environment variables: Keep secure backups of `.env` files locally

---

## Troubleshooting

### Issue 1: Containers Won't Start

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common causes:**
- Port conflicts (something else using port 80 or 5000)
- Environment variables missing
- Database connection failure

**Solutions:**
```bash
# Check what's using ports
sudo lsof -i :80
sudo lsof -i :5000

# Kill conflicting processes
sudo kill -9 <PID>

# Restart Docker
sudo systemctl restart docker
docker-compose up -d --force-recreate
```

### Issue 2: Cannot Connect to RDS Database

**Check security groups:**
- EC2 security group must allow outbound traffic on port 3306
- RDS security group must allow inbound from EC2 security group

**Test connection:**
```bash
# Install MySQL client
sudo apt-get install -y mysql-client

# Test connection
mysql -h mooddj-database.c9wc8gkmgine.ca-central-1.rds.amazonaws.com -u admin -p
```

### Issue 3: Frontend Shows "Cannot connect to backend"

**Check backend status:**
```bash
curl http://localhost:5000/api/health
```

**Check CORS settings:**
- Backend CORS must allow frontend domain
- Update `backend/app.py` CORS origins

### Issue 4: OAuth Callback Fails

**Verify Spotify settings:**
1. Redirect URI in Spotify Dashboard matches exactly
2. Format: `http://yourdomain.com:5000/api/auth/callback`
3. No trailing slashes

**Check environment variables:**
```bash
docker-compose exec backend env | grep SPOTIFY
```

### Issue 5: High Memory Usage

**Check memory:**
```bash
free -h
docker stats
```

**Solutions:**
- Restart containers: `docker-compose restart`
- Increase EC2 instance size if consistently high
- Limit container resources in docker-compose.yml

### Issue 6: Website Not Accessible from Browser

**Check EC2 security group:**
- Port 80 must allow 0.0.0.0/0
- Port 5000 must allow 0.0.0.0/0

**Check if containers are running:**
```bash
docker-compose ps
```

**Check if ports are listening:**
```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000
```

---

## Cost Breakdown

**Monthly Costs for Current Setup:**

| Service | Configuration | Cost | Notes |
|---------|--------------|------|-------|
| **EC2 Instance** | t2.small (1 vCPU, 2GB RAM) | ~$17 | On-demand pricing |
| **EC2 Instance** | t2.medium (2 vCPU, 4GB RAM) | ~$34 | Better performance |
| **RDS MySQL** | db.t3.micro (1 vCPU, 1GB RAM) | ~$15 | Can use free tier for 12 months |
| **EBS Storage** | 20-30 GB gp3 | ~$2-3 | Block storage for EC2 |
| **Data Transfer** | Outbound internet traffic | ~$1-5 | First 1 GB free |
| **Elastic IP** | If using static IP | $0 | Free when associated with running instance |
| **Domain (GoDaddy)** | Already purchased | ~$12/year | Paid annually |
| **Backups/Snapshots** | Manual RDS snapshots | ~$0-2 | Only if creating extras |

**Total Monthly Cost:**
- **With t2.small:** ~$35-42/month
- **With t2.medium:** ~$52-59/month
- **First year with RDS free tier:** ~$20-25/month less

**Cost Optimization Tips:**
1. Use t2.small for MVP (can upgrade later)
2. Enable RDS free tier if eligible
3. Set up CloudWatch alarms to monitor usage
4. Use EC2 Reserved Instances for 1-year commitment (40% savings)
5. Schedule EC2 stop/start if not 24/7 (can reduce costs by 50%)

---

## Performance Optimization

### 1. Enable HTTP/2 and Compression

Already enabled in `mooddj-frontend/nginx.conf`:
- Gzip compression
- Static asset caching
- Security headers

### 2. Frontend Build Optimization

```bash
# On EC2, build with optimizations
cd ~/MoodDJ/mooddj-frontend
npm run build
```

### 3. Backend Performance

**Use Gunicorn in production:**

Update `backend/Dockerfile` to use:
```dockerfile
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

### 4. Database Query Optimization

- Index frequently queried columns
- Use connection pooling (already implemented)
- Cache audio features in Redis (future improvement)

### 5. Monitoring

**Install CloudWatch Agent (Optional):**
```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

---

## Security Hardening

### 1. Update SSH Configuration

```bash
sudo nano /etc/ssh/sshd_config
```

Recommended settings:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### 2. Keep System Updated

```bash
# Run weekly
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Enable HTTPS with Let's Encrypt (Future)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

### 4. Environment Variable Security

- Never commit `.env` files to GitHub
- Use AWS Secrets Manager for production (advanced)
- Rotate API keys regularly

---

## Migration Path to ECS/Kubernetes (Future)

If you outgrow EC2, here's the migration path:

### To AWS ECS Fargate:
1. Push Docker images to ECR
2. Create ECS Task Definitions
3. Set up ALB
4. Deploy ECS Service
5. Update DNS

**Estimated effort:** 1-2 days
**Cost increase:** +$30-50/month

### To Kubernetes (EKS):
1. Create Kubernetes manifests
2. Set up EKS cluster
3. Deploy with kubectl
4. Configure ingress

**Estimated effort:** 3-5 days
**Cost increase:** +$70-100/month

---

## Next Steps

### Immediate:
- ✅ Application is deployed and running
- ✅ Domain pointing to EC2
- ✅ OAuth configured
- ✅ Database connected

### Short-term (1-2 weeks):
- [ ] Set up HTTPS with Let's Encrypt
- [ ] Configure automated backups
- [ ] Add monitoring and alerts
- [ ] Create CI/CD pipeline for automated deployments

### Medium-term (1-2 months):
- [ ] Implement Redis for session storage
- [ ] Add caching for API responses
- [ ] Set up CDN for static assets
- [ ] Add analytics and user tracking

### Long-term (3+ months):
- [ ] Scale to multiple EC2 instances with load balancer
- [ ] Migrate to ECS Fargate for better scalability
- [ ] Implement auto-scaling
- [ ] Add comprehensive testing suite

---

## Support Resources

**AWS Documentation:**
- EC2: https://docs.aws.amazon.com/ec2/
- RDS: https://docs.aws.amazon.com/rds/
- Docker: https://docs.docker.com/

**Project Documentation:**
- README: See project README.md
- Development Log: See DEVELOPMENT_LOG.md
- API Documentation: Check backend/routes/ files

**Getting Help:**
- GitHub Issues: https://github.com/WashimAkram027/MoodDJ/issues
- AWS Support: Use AWS Console support
- Stack Overflow: Tag questions with aws, docker, flask, react

---

## Deployment Checklist

Before going live:

- [ ] All environment variables configured correctly
- [ ] Database connection tested
- [ ] Spotify OAuth working with production URL
- [ ] Frontend can communicate with backend
- [ ] Domain/DNS configured and propagated
- [ ] Security groups properly configured
- [ ] Firewall enabled on EC2
- [ ] HTTPS configured (or planned)
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team members have access to EC2 key
- [ ] Costs reviewed and acceptable

---

**Congratulations!** You have successfully deployed MoodDJ to AWS EC2 with a simple, cost-effective containerized approach. This setup is perfect for MVP, demos, and small-to-medium traffic, and can easily scale up when needed.

**Instance Access:**
- SSH: `ssh -i mooddj-key.pem ubuntu@<EC2_IP>`
- Instance Name: mooddj-prod
- Region: ca-central-1
- Database: mooddj-database.c9wc8gkmgine.ca-central-1.rds.amazonaws.com
