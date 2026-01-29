# GitHub Webhook Receiver

A Flask-based application that receives GitHub webhook events (PUSH, PULL_REQUEST, MERGE), stores them in MongoDB, and displays them in a real-time UI.

## Features

- ✅ Receives GitHub webhooks for PUSH, PULL_REQUEST, and MERGE events
- ✅ Stores event data in MongoDB with proper schema
- ✅ Real-time UI that polls MongoDB every 15 seconds
- ✅ Clean, minimal, and responsive design
- ✅ Proper error handling and logging
- ✅ Webhook signature verification for security
- ✅ Prevents duplicate event display on refresh

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Deployment Ready**: Gunicorn for production

## Project Structure

```
webhook-repo/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # UI template
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## MongoDB Schema

```javascript
{
  "_id": ObjectId,           // MongoDB default ID
  "request_id": String,      // Commit hash (PUSH) or PR number (PULL_REQUEST/MERGE)
  "author": String,          // GitHub username
  "action": String,          // "PUSH", "PULL_REQUEST", or "MERGE"
  "from_branch": String,     // Source branch
  "to_branch": String,       // Target branch
  "timestamp": String        // ISO 8601 datetime string (UTC)
}
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance like MongoDB Atlas)
- Git

### 1. Clone the Repository

```bash
git clone <your-webhook-repo-url>
cd webhook-repo
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=github_webhooks
COLLECTION_NAME=events
WEBHOOK_SECRET=your_secret_here  # Optional but recommended
PORT=5000
```

### 5. Start MongoDB

Make sure MongoDB is running:

```bash
# On macOS with Homebrew
brew services start mongodb-community

# On Linux
sudo systemctl start mongod

# Or use MongoDB Atlas (cloud) and update MONGO_URI
```

### 6. Run the Application

```bash
# Development mode
python app.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The application will be available at `http://localhost:5000`

## Setting Up GitHub Webhooks

### 1. Expose Your Local Server (for testing)

Use a tool like ngrok to expose your local server:

```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 2. Configure Webhook in GitHub

1. Go to your `action-repo` repository on GitHub
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-ngrok-url.ngrok.io/webhook`
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret (same as in `.env`)
   - **Events**: Select "Let me select individual events"
     - ✅ Pushes
     - ✅ Pull requests
   - **Active**: ✅ Checked

4. Click **Add webhook**

### 3. Test the Webhook

Trigger events in your `action-repo`:

```bash
# Test PUSH event
echo "test" > test.txt
git add test.txt
git commit -m "Test push event"
git push origin main

# Test PULL_REQUEST event
git checkout -b feature-branch
echo "feature" > feature.txt
git add feature.txt
git commit -m "Add feature"
git push origin feature-branch
# Then create a PR on GitHub

# Test MERGE event
# Merge the PR on GitHub
```

## API Endpoints

### `GET /`
Returns the main UI page

### `POST /webhook`
GitHub webhook endpoint
- Headers: `X-GitHub-Event`, `X-Hub-Signature-256`
- Body: GitHub webhook payload (JSON)

### `GET /api/events`
Fetch all events from MongoDB
- Response: Array of event objects (sorted by timestamp, descending)

### `POST /api/events/clear`
Clear all events (useful for testing)
- Response: `{status: 'success', deleted_count: number}`

### `GET /health`
Health check endpoint
- Response: `{status: 'healthy'}`

## Event Display Formats

### PUSH Event
```
{author} pushed to {to_branch} on {timestamp}
```
Example: *Travis pushed to "staging" on 1st April 2021 - 9:30 PM UTC*

### PULL_REQUEST Event
```
{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}
```
Example: *Travis submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC*

### MERGE Event (Brownie Points!)
```
{author} merged branch {from_branch} to {to_branch} on {timestamp}
```
Example: *Travis merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC*

## Features Implemented

✅ **Proper Code Structure**: Modular functions, clear separation of concerns  
✅ **Error Handling**: Try-catch blocks, proper logging  
✅ **Security**: Webhook signature verification  
✅ **Documentation**: Comprehensive comments and docstrings  
✅ **Data Validation**: Timestamp formatting, proper data parsing  
✅ **No Duplicate Display**: Tracks displayed events to avoid showing duplicates  
✅ **Clean UI**: Minimal, responsive design with auto-refresh  
✅ **Production Ready**: Gunicorn configuration included  

## Deployment

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Set environment variables
heroku config:set WEBHOOK_SECRET=your_secret

# Deploy
git push heroku main

# Open app
heroku open
```

### Deploy to Railway/Render

1. Connect your GitHub repository
2. Add MongoDB database
3. Set environment variables
4. Deploy automatically

## Testing Checklist

- [ ] PUSH events are captured correctly
- [ ] PULL_REQUEST events are captured correctly
- [ ] MERGE events are captured correctly (brownie points!)
- [ ] UI displays all events properly
- [ ] UI refreshes every 15 seconds
- [ ] No duplicate events on refresh
- [ ] Timestamps are formatted correctly in UTC
- [ ] Branch names display correctly
- [ ] Author names display correctly
- [ ] UI is responsive on mobile devices

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running
- Check `MONGO_URI` in `.env`
- For Atlas, whitelist your IP address

### Webhook Not Receiving Events
- Check ngrok is running
- Verify webhook URL in GitHub settings
- Check GitHub webhook delivery logs
- Verify webhook secret matches

### UI Not Updating
- Check browser console for errors
- Verify `/api/events` endpoint returns data
- Clear browser cache

## Author

Created for TechStax Developer Assessment

## License

MIT License
