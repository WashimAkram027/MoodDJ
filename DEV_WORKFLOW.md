# MoodDJ Development & Deployment Workflow
**Quick Guide for Making Changes and Deploying**

**Last Updated:** 2025-01-16

---

## Overview

This guide covers the workflow for making changes (frontend or backend), testing locally, and deploying to production EC2.

---

## Quick Reference

| Task | Command | Where |
|------|---------|-------|
| **Local development (frontend)** | `npm start` | `mooddj-frontend/` |
| **Local development (backend)** | `python app.py` | `backend/` (with venv) |
| **Test with Docker** | `docker-compose up --build` | Project root |
| **Deploy to EC2** | SSH + `git pull` + rebuild | EC2 instance |

---

## Development Workflow Options

### Option 1: Local Development (Fastest) ⚡ RECOMMENDED

**Use this for:** Quick UI changes, testing features, rapid iteration

#### Frontend Changes (React/UI)

```bash
# 1. Navigate to frontend
cd mooddj-frontend

# 2. Install dependencies (first time only)
npm install

# 3. Start development server
npm start

# Browser automatically opens at http://localhost:3000
# Hot reload enabled - changes appear instantly
```

**Features:**
- ✅ Instant hot reload on file save
- ✅ Fast feedback loop
- ✅ React DevTools available
- ✅ No Docker overhead

**What it connects to:**
- Backend: `http://127.0.0.1:5000` (from `.env`)
- Database: AWS RDS (via backend)

#### Backend Changes (Python/Flask)

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies (first time only)
pip install -r requirements.txt

# 4. Run Flask development server
python app.py

# Server starts at http://0.0.0.0:5000
# Auto-reloads on file changes (Flask debug mode)
```

**Features:**
- ✅ Auto-reload on code changes
- ✅ Debug mode with detailed errors
- ✅ Fast startup
- ✅ Direct access to logs

**What it connects to:**
- Database: AWS RDS (from `.env`)
- RapidAPI: Production API
- Spotify: Production OAuth

---

### Option 2: Docker Development (Production-like) 🐳

**Use this for:** Testing containerized behavior, verifying production setup

```bash
# 1. Navigate to project root
cd MoodDJ

# 2. Build and run all services
docker-compose up --build

# Wait for services to start (~1-2 minutes)
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

**To rebuild after changes:**
```bash
# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up --build

# Or rebuild specific service:
docker-compose up --build frontend
docker-compose up --build backend
```

**Features:**
- ✅ Exact production environment
- ✅ Tests Docker configuration
- ✅ Verifies container networking
- ⚠️ Slower rebuild time
- ⚠️ No hot reload

**When to use Docker:**
- Before deploying to EC2 (verify Docker works)
- Testing environment variables
- Debugging container issues
- Testing production-like setup

---

## Complete Development Workflow

### Making Frontend Changes

```bash
# Step 1: Make your changes
# Edit files in mooddj-frontend/src/

# Step 2: Test locally (fast)
cd mooddj-frontend
npm start
# Browser opens, test your changes

# Step 3: Verify with Docker (optional but recommended)
cd ..
docker-compose up --build frontend
# Access at http://localhost:3000
# Test that it works in Docker

# Step 4: Commit changes
git add mooddj-frontend/
git commit -m "Update: [description of changes]"
git push origin washimbranch  # or main

# Step 5: Deploy to EC2 (see deployment section below)
```

### Making Backend Changes

```bash
# Step 1: Make your changes
# Edit files in backend/

# Step 2: Test locally (fast)
cd backend
venv\Scripts\activate  # Windows
python app.py
# Test API at http://localhost:5000

# Step 3: Verify with Docker (optional but recommended)
cd ..
docker-compose up --build backend
# Test that it works in Docker

# Step 4: Commit changes
git add backend/
git commit -m "Update: [description of changes]"
git push origin washimbranch  # or main

# Step 5: Deploy to EC2 (see deployment section below)
```

---

## Deployment to EC2

### Prerequisites
- Changes committed and pushed to GitHub
- Tested locally (with or without Docker)
- EC2 instance running
- SSH key available (`mooddj-key.pem`)

### Deployment Process

#### Option A: Manual Deployment (Step-by-step)

```bash
# 1. SSH into EC2
ssh -i mooddj-key.pem ubuntu@<EC2_PUBLIC_IP>
# Or if using domain:
ssh -i mooddj-key.pem ubuntu@<YOUR_DOMAIN>

# 2. Navigate to project directory
cd ~/MoodDJ

# 3. Check current status
docker-compose ps
git status

# 4. Pull latest changes
git pull origin washimbranch  # or main

# 5. Stop current containers
docker-compose down

# 6. Rebuild and restart
docker-compose up -d --build

# 7. Verify deployment
docker-compose ps
docker-compose logs -f

# 8. Test in browser
# Visit http://<EC2_IP> or http://<YOUR_DOMAIN>
# Test the changes you made

# 9. Exit SSH
exit
```

**Time:** ~5 minutes

#### Option B: Quick Deployment (One-liner)

```bash
# From your local machine
ssh -i mooddj-key.pem ubuntu@<EC2_IP> "cd ~/MoodDJ && git pull && docker-compose down && docker-compose up -d --build"
```

#### Option C: Deployment Script (Recommended)

Create a deployment script on EC2 for easy updates:

```bash
# One-time setup: Create deploy script on EC2
ssh -i mooddj-key.pem ubuntu@<EC2_IP>

cat > ~/MoodDJ/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting MoodDJ deployment..."

# Navigate to project
cd ~/MoodDJ

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull

# Check for changes
if [ $? -ne 0 ]; then
    echo "❌ Git pull failed! Check for conflicts."
    exit 1
fi

# Stop containers
echo "🛑 Stopping containers..."
docker-compose down

# Rebuild and start
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check status
echo "✅ Deployment complete! Service status:"
docker-compose ps

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=50

echo "🎉 Deployment successful!"
EOF

chmod +x ~/MoodDJ/deploy.sh
exit
```

**Usage:**
```bash
# From local machine
ssh -i mooddj-key.pem ubuntu@<EC2_IP> "~/MoodDJ/deploy.sh"
```

---

## Testing Changes Before Deployment

### Quick Testing Checklist

Before deploying, verify:

#### Frontend Changes
- [ ] `npm start` works locally
- [ ] No console errors in browser
- [ ] UI looks correct
- [ ] API calls work (check Network tab)
- [ ] OAuth login works (if affected)
- [ ] Camera permissions work (if affected)

#### Backend Changes
- [ ] `python app.py` runs without errors
- [ ] API endpoints respond correctly
- [ ] Database queries work
- [ ] No breaking changes to API contracts
- [ ] OAuth callback works (if affected)

#### Docker Verification (Optional but Recommended)
- [ ] `docker-compose up --build` succeeds
- [ ] No build errors
- [ ] Services start successfully
- [ ] Frontend accessible at localhost:3000
- [ ] Backend accessible at localhost:5000
- [ ] Full workflow works in Docker

---

## Common Development Scenarios

### Scenario 1: Changing UI Colors/Styles

```bash
# 1. Edit CSS/component files
cd mooddj-frontend/src
# Make your changes

# 2. See changes instantly (npm start is running)
# No restart needed

# 3. When satisfied, commit and deploy
git add .
git commit -m "Update UI colors"
git push
# Then deploy to EC2
```

### Scenario 2: Adding New API Endpoint

```bash
# 1. Add endpoint to backend/routes/
cd backend/routes
# Edit relevant route file

# 2. Test locally
cd ..
venv\Scripts\activate
python app.py
# Test endpoint: http://localhost:5000/api/your-new-endpoint

# 3. Update frontend to use new endpoint
cd ../mooddj-frontend/src/services
# Edit API service file

# 4. Test full flow locally
npm start  # In separate terminal

# 5. Verify with Docker
cd ../..
docker-compose up --build

# 6. Deploy to EC2
```

### Scenario 3: Updating Dependencies

```bash
# Frontend dependency
cd mooddj-frontend
npm install <package-name>
npm start  # Test it works

# Backend dependency
cd ../backend
venv\Scripts\activate
pip install <package-name>
pip freeze > requirements.txt  # Update requirements
python app.py  # Test it works

# Deploy with Docker (will install new dependencies)
cd ..
docker-compose up --build
```

### Scenario 4: Environment Variable Changes

```bash
# 1. Update .env file
cd backend
nano .env  # Or edit in VS Code

# 2. Restart Flask
python app.py

# 3. Update docker-compose.yml if needed
cd ..
nano docker-compose.yml

# 4. Test with Docker
docker-compose up --build

# 5. Update .env on EC2
ssh -i mooddj-key.pem ubuntu@<EC2_IP>
cd ~/MoodDJ/backend
nano .env
# Make same changes
exit

# 6. Deploy
ssh -i mooddj-key.pem ubuntu@<EC2_IP> "~/MoodDJ/deploy.sh"
```

---

## Rollback Process

If deployment breaks:

```bash
# Option 1: Quick rollback via git
ssh -i mooddj-key.pem ubuntu@<EC2_IP>
cd ~/MoodDJ
git log --oneline -5  # Find previous working commit
git checkout <commit-hash>
docker-compose down && docker-compose up -d --build
exit

# Option 2: Force previous image (if recently deployed)
ssh -i mooddj-key.pem ubuntu@<EC2_IP>
cd ~/MoodDJ
docker-compose down
docker-compose up -d  # Without --build uses cached image
exit
```

---

## Recommended Workflow

### Daily Development:

1. **Work locally** with `npm start` (frontend) or `python app.py` (backend)
2. **Test changes** in browser/Postman
3. **Commit often** to git
4. **Test with Docker** before pushing (optional but recommended)
5. **Push to GitHub**
6. **Deploy to EC2** when ready

### Before Each Deployment:

1. ✅ Test locally
2. ✅ Test with Docker (optional)
3. ✅ Commit and push to GitHub
4. ✅ Pull on EC2
5. ✅ Rebuild containers
6. ✅ Verify in browser
7. ✅ Monitor logs

---

## Best Practices

### Local Development
- Keep `npm start` or `python app.py` running for hot reload
- Use browser DevTools for debugging
- Test API changes with Postman or curl
- Check logs frequently

### Docker Testing
- Always rebuild after major changes: `docker-compose up --build`
- Check logs: `docker-compose logs -f`
- Verify both services: `docker-compose ps`

### Deployment
- Deploy during low-traffic times
- Test immediately after deployment
- Keep an eye on logs: `docker-compose logs -f backend`
- Have rollback plan ready

### Version Control
- Commit after each logical change
- Write clear commit messages
- Use meaningful branch names
- Don't commit `.env` files (already in .gitignore)

---

## Troubleshooting

### "Changes don't appear after deployment"

```bash
# Force rebuild without cache
ssh -i mooddj-key.pem ubuntu@<EC2_IP>
cd ~/MoodDJ
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### "Container won't start after update"

```bash
# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Common issues:
# - Syntax error in code
# - Missing dependency in requirements.txt or package.json
# - Port conflict
# - Database connection issue
```

### "Frontend shows old version"

```bash
# Browser cache - hard refresh
# Chrome/Firefox: Ctrl+Shift+R
# Or clear browser cache

# On EC2, verify React rebuild:
docker-compose logs frontend
# Should see "npm run build" output
```

### "Backend changes not working"

```bash
# Verify backend container rebuilt
docker-compose ps
docker-compose logs backend

# Check if .env changes are needed
docker-compose exec backend env | grep <VAR_NAME>
```

---

## Time Estimates

| Task | Local Development | Docker Testing | Deployment |
|------|-------------------|----------------|------------|
| **Small UI change** | Instant (hot reload) | 2-3 min | 5 min |
| **Backend endpoint** | 30 sec (restart) | 2-3 min | 5 min |
| **Dependency update** | 1-2 min | 3-5 min | 5-7 min |
| **Major feature** | Varies | 5 min | 5-10 min |

---

## Summary

**Fastest development workflow:**
1. Edit code
2. Test locally (`npm start` or `python app.py`)
3. Verify changes
4. Push to GitHub
5. Deploy to EC2 (pull + rebuild)

**When to use Docker locally:**
- Before major deployments
- Testing environment changes
- Debugging container issues
- Verifying production-like behavior

**Remember:** Local development is fastest for iteration, Docker testing ensures production compatibility, EC2 deployment is straightforward with the deployment script.

---

**Next Steps:**
- Set up deployment script on EC2 (one-time)
- Bookmark this workflow guide
- Start developing with confidence! 🚀
