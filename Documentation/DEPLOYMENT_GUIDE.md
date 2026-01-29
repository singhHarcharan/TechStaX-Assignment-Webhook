# Complete Deployment & Submission Guide

This guide will walk you through setting up, deploying, and submitting your TechStax Developer Assessment.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [GitHub Repositories Setup](#github-repositories-setup)
4. [MongoDB Setup](#mongodb-setup)
5. [Deployment Options](#deployment-options)
6. [Testing](#testing)
7. [Submission](#submission)

---

## Prerequisites

### Required Software

- **Git**: [Download Git](https://git-scm.com/downloads)
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **MongoDB**: Choose one option:
  - [MongoDB Community (Local)](https://www.mongodb.com/try/download/community)
  - [MongoDB Atlas (Cloud - Free)](https://www.mongodb.com/cloud/atlas/register)

### Required Accounts

- **GitHub Account**: [Sign up](https://github.com/join)
- **Deployment Platform** (choose one):
  - [Heroku](https://signup.heroku.com/) (Recommended)
  - [Railway](https://railway.app/)
  - [Render](https://render.com/)

---

## Local Setup

### 1. Set Up webhook-repo

```bash
# Navigate to webhook-repo directory
cd webhook-repo

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
# Use a text editor to modify:
# - MONGO_URI (from MongoDB setup)
# - WEBHOOK_SECRET (generate a random string)
```

### 2. Generate Webhook Secret

```bash
# Generate a random secret
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and add it to your .env file
```

---

## MongoDB Setup

### Option A: MongoDB Atlas (Cloud - Recommended)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create a free account
3. Create a new cluster (M0 Free tier)
4. Click "Connect" → "Connect your application"
5. Copy the connection string
6. Replace `<password>` with your database password
7. Update `MONGO_URI` in `.env`:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/github_webhooks?retryWrites=true&w=majority
   ```
8. In Atlas, go to "Network Access" → "Add IP Address" → "Allow Access from Anywhere"

### Option B: Local MongoDB

```bash
# On macOS (using Homebrew)
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# On Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# On Windows
# Download and install from: https://www.mongodb.com/try/download/community
# MongoDB will start automatically as a service

# Update .env
MONGO_URI=mongodb://localhost:27017/
```

---

## GitHub Repositories Setup

### 1. Create action-repo

```bash
# Navigate to action-repo directory
cd action-repo

# Initialize git
git init
git add .
git commit -m "Initial commit: Setup action repository"

# Create repository on GitHub
# Go to: https://github.com/new
# Repository name: action-repo
# Make it Public
# Don't initialize with README (we already have files)

# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/action-repo.git
git branch -M main
git push -u origin main
```

### 2. Create webhook-repo

```bash
# Navigate to webhook-repo directory
cd webhook-repo

# Initialize git
git init
git add .
git commit -m "Initial commit: Flask webhook receiver"

# Create repository on GitHub
# Go to: https://github.com/new
# Repository name: webhook-repo
# Make it Public

# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/webhook-repo.git
git branch -M main
git push -u origin main
```

---

## Deployment Options

### Option 1: Heroku (Recommended)

#### Install Heroku CLI

- **macOS**: `brew install heroku/brew/heroku`
- **Windows**: [Download installer](https://devcenter.heroku.com/articles/heroku-cli)
- **Linux**: `curl https://cli-assets.heroku.com/install.sh | sh`

#### Deploy webhook-repo

```bash
# Login to Heroku
heroku login

# Create Heroku app
cd webhook-repo
heroku create your-app-name-webhook

# Add MongoDB addon (or use Atlas)
heroku addons:create mongolab:sandbox

# OR set MongoDB Atlas URI
heroku config:set MONGO_URI="your_mongodb_atlas_uri"

# Set webhook secret
heroku config:set WEBHOOK_SECRET="your_generated_secret"

# Deploy
git push heroku main

# Open your app
heroku open

# View logs
heroku logs --tail
```

Your webhook URL will be: `https://your-app-name-webhook.herokuapp.com/webhook`

### Option 2: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# OR deploy via web
# Go to: https://railway.app/new
# Click "Deploy from GitHub repo"
# Select webhook-repo
# Add MongoDB plugin
# Set environment variables:
#   - WEBHOOK_SECRET
# Deploy
```

### Option 3: Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub webhook-repo
4. Configure:
   - **Name**: webhook-receiver
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variables:
   - `MONGO_URI`
   - `WEBHOOK_SECRET`
6. Click "Create Web Service"

---

## Testing

### 1. Test Locally (Optional)

```bash
# Start Flask app
cd webhook-repo
python app.py

# In another terminal, use ngrok
ngrok http 5001

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
```

### 2. Configure GitHub Webhook

1. Go to your `action-repo` on GitHub
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-deployment-url.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret (same as in deployment)
   - **Which events**: Select "Let me select individual events"
     - ✅ Pushes
     - ✅ Pull requests
   - **Active**: ✅ Checked
4. Click **Add webhook**

### 3. Trigger Test Events

#### Test PUSH Event

```bash
cd action-repo

# Make a change
echo "Test push: $(date)" >> test.txt
git add test.txt
git commit -m "Test PUSH webhook event"
git push origin main
```

#### Test PULL_REQUEST Event

```bash
# Create feature branch
git checkout -b feature/test-webhook
echo "Test feature" >> feature.txt
git add feature.txt
git commit -m "Add test feature"
git push origin feature/test-webhook

# Go to GitHub and create a Pull Request
# From: feature/test-webhook → To: main
```

#### Test MERGE Event (Brownie Points!)

1. Go to your Pull Request on GitHub
2. Click **"Merge pull request"**
3. Click **"Confirm merge"**

### 4. Verify Events

1. **Check GitHub Webhook Deliveries**:
   - Go to your webhook settings
   - Click on your webhook
   - Go to "Recent Deliveries" tab
   - Verify status is `200` for recent events

2. **Check Your Application**:
   - Open your deployed URL (e.g., `https://your-app-name.herokuapp.com`)
   - Verify events appear in the UI
   - Check that:
     - ✅ Event types are correct (PUSH, PULL_REQUEST, MERGE)
     - ✅ Author names are displayed
     - ✅ Branch names are correct
     - ✅ Timestamps are in UTC format
     - ✅ No duplicate events on refresh

3. **Check Logs**:
   ```bash
   # Heroku
   heroku logs --tail
   
   # Railway
   railway logs
   
   # Render
   # Check logs in dashboard
   ```

---

## Submission

### Pre-Submission Checklist

- [ ] Both repositories (`action-repo` and `webhook-repo`) are created on GitHub
- [ ] Both repositories are **Public**
- [ ] webhook-repo is deployed and accessible
- [ ] GitHub webhook is configured correctly
- [ ] All three event types are tested and working:
  - [ ] PUSH events
  - [ ] PULL_REQUEST events
  - [ ] MERGE events (brownie points!)
- [ ] UI displays events correctly with proper formatting
- [ ] UI refreshes every 15 seconds automatically
- [ ] Code has proper comments and documentation
- [ ] README files are complete in both repositories

### Submission Information to Provide

Prepare the following information for the Google Form:

1. **action-repo URL**: `https://github.com/YOUR_USERNAME/action-repo`
2. **webhook-repo URL**: `https://github.com/YOUR_USERNAME/webhook-repo`
3. **Deployed Application URL**: `https://your-app-name.herokuapp.com`
4. **Screenshots** (optional but helpful):
   - Screenshot of GitHub webhook configuration
   - Screenshot of your UI showing events
   - Screenshot of webhook delivery success

### Submit via Google Form

1. Go to: [forms.gle/qkdB1GVVkjqK7ytc7](https://forms.gle/qkdB1GVVkjqK7ytc7)
2. Fill in all required information
3. Provide both GitHub repository links
4. Submit before: **30 Jan, 2026 23:59:59**

---

## Common Issues & Solutions

### Issue: Webhook Returns 401/403

**Solution**: 
- Verify webhook secret matches in GitHub and your deployment
- Check environment variable is set correctly: `heroku config` or check deployment dashboard

### Issue: Events Not Appearing in UI

**Solution**:
- Check MongoDB connection: Review application logs
- Verify webhook is being triggered: Check GitHub webhook delivery logs
- Check browser console for JavaScript errors

### Issue: MongoDB Connection Failed

**Solution**:
- For Atlas: Verify IP is whitelisted (allow 0.0.0.0/0)
- For Atlas: Verify connection string is correct
- Check `MONGO_URI` environment variable

### Issue: UI Shows Old Events After Refresh

**Solution**:
- This is expected behavior (prevents duplicates)
- To test fresh, use the clear events endpoint: `POST /api/events/clear`
- Or clear MongoDB collection directly

### Issue: Deployment Failed

**Solution**:
- Verify `requirements.txt` includes all dependencies
- Check `Procfile` is present (for Heroku)
- Review deployment logs for specific errors
- Ensure Python version is compatible

---

## Code Quality Highlights

### ✅ Industry Best Practices

1. **Clean Code Structure**
   - Modular functions
   - Clear separation of concerns
   - Descriptive variable names

2. **Error Handling**
   - Try-catch blocks for all critical operations
   - Comprehensive logging
   - Graceful error responses

3. **Security**
   - Webhook signature verification
   - Environment variables for secrets
   - Input validation

4. **Documentation**
   - Detailed comments
   - Comprehensive README files
   - API endpoint documentation

5. **User Experience**
   - Clean, minimal UI design
   - Real-time updates (15s polling)
   - Responsive design
   - No duplicate display logic

6. **Production Ready**
   - Gunicorn for production server
   - Deployment configurations included
   - Health check endpoint

---

## Final Notes

- Keep your repositories **public** so reviewers can access them
- Test all three event types before submission
- Make sure your deployed application is accessible
- Don't forget to implement MERGE event handling (brownie points!)
- Submit before the deadline: **30 Jan, 2026 23:59:59**

Good luck with your submission! 🚀

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review application logs
3. Verify GitHub webhook delivery logs
4. Test locally with ngrok first

Remember: The assignment tests your ability to:
- Work with webhooks
- Store data properly
- Display data cleanly
- Write production-quality code
