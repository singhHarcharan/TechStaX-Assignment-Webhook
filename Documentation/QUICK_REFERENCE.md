# Quick Reference Cheat Sheet

## 🚀 Quick Start Commands

### Local Development

```bash
# Setup webhook-repo
cd webhook-repo
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI
python app.py
```

### GitHub Setup

```bash
# Setup action-repo
cd action-repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/action-repo.git
git push -u origin main

# Setup webhook-repo
cd webhook-repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/webhook-repo.git
git push -u origin main
```

### Deploy to Heroku

```bash
cd webhook-repo
heroku login
heroku create your-app-name
heroku config:set MONGO_URI="your_mongodb_uri"
heroku config:set WEBHOOK_SECRET="your_secret"
git push heroku main
heroku open
```

## 📝 Event Formats

### PUSH Event
```
{author} pushed to {to_branch} on {timestamp}
Example: "Travis pushed to staging on 1st April 2021 - 9:30 PM UTC"
```

### PULL_REQUEST Event
```
{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}
Example: "Travis submitted a pull request from staging to master on 1st April 2021 - 9:00 AM UTC"
```

### MERGE Event
```
{author} merged branch {from_branch} to {to_branch} on {timestamp}
Example: "Travis merged branch dev to master on 2nd April 2021 - 12:00 PM UTC"
```

## 🔧 Testing Commands

### Trigger PUSH Event
```bash
cd action-repo
echo "Test: $(date)" >> test.txt
git add test.txt
git commit -m "Test PUSH event"
git push origin main
```

### Trigger PULL_REQUEST Event
```bash
cd action-repo
git checkout -b feature/test
echo "Feature" >> feature.txt
git add feature.txt
git commit -m "Add feature"
git push origin feature/test
# Create PR on GitHub
```

### Trigger MERGE Event
```bash
# Merge the PR on GitHub UI
```

### Test Locally
```bash
cd webhook-repo
python test_webhook.py
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | UI page |
| POST | `/webhook` | GitHub webhook receiver |
| GET | `/api/events` | Get all events |
| POST | `/api/events/clear` | Clear all events |
| GET | `/health` | Health check |

## 🔍 Debugging

### Check Heroku Logs
```bash
heroku logs --tail
```

### Check Webhook Deliveries
```
GitHub → Settings → Webhooks → Recent Deliveries
```

### Test MongoDB Connection
```python
from pymongo import MongoClient
client = MongoClient("your_mongo_uri")
db = client.github_webhooks
print(db.list_collection_names())
```

## 📊 MongoDB Schema

```javascript
{
  "_id": ObjectId("..."),
  "request_id": "abc123",
  "author": "username",
  "action": "PUSH",
  "from_branch": "main",
  "to_branch": "main",
  "timestamp": "2021-04-01T21:30:00Z"
}
```

## ✅ Submission Checklist

- [ ] action-repo created and pushed to GitHub
- [ ] webhook-repo created and pushed to GitHub
- [ ] Both repos are PUBLIC
- [ ] Application deployed (Heroku/Railway/Render)
- [ ] MongoDB connected (Atlas or local)
- [ ] GitHub webhook configured in action-repo
- [ ] PUSH events working
- [ ] PULL_REQUEST events working
- [ ] MERGE events working (brownie points!)
- [ ] UI showing events correctly
- [ ] UI auto-refreshes every 15 seconds
- [ ] No duplicate events on refresh
- [ ] Code has proper comments
- [ ] README files complete

## 📦 What to Submit

1. **action-repo URL**: `https://github.com/USERNAME/action-repo`
2. **webhook-repo URL**: `https://github.com/USERNAME/webhook-repo`
3. **Deployed URL**: `https://your-app.herokuapp.com`

## 🎯 Key Features Implemented

✅ Webhook signature verification  
✅ Proper error handling  
✅ Comprehensive logging  
✅ Clean UI design  
✅ Auto-refresh (15s polling)  
✅ No duplicate display  
✅ UTC timestamp formatting  
✅ MongoDB schema compliance  
✅ Production-ready (Gunicorn)  
✅ MERGE event handling (brownie points!)  

## ⏰ Deadline

**30 Jan, 2026 23:59:59**

Submit at: [forms.gle/qkdB1GVVkjqK7ytc7](https://forms.gle/qkdB1GVVkjqK7ytc7)

## 🆘 Common Issues

**Webhook 401**: Check webhook secret matches  
**No events**: Check MongoDB connection  
**CORS error**: Flask-CORS is installed  
**Deployment fails**: Check Procfile and requirements.txt  
**Events not showing**: Check browser console  

## 📞 Environment Variables

```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
DATABASE_NAME=github_webhooks
COLLECTION_NAME=events
WEBHOOK_SECRET=your_secret_here
PORT=5000
```

## 🔐 Generate Webhook Secret

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🎨 UI Features

- Clean, minimal design
- Responsive (mobile-friendly)
- Color-coded event types
- Real-time updates
- Event counter
- Last update timestamp
- Animated transitions

Good luck! 🚀
