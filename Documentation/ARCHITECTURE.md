# System Architecture Overview

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub (action-repo)                        │
│  - PUSH events (commits)                                            │
│  - PULL_REQUEST events (open PRs)                                   │
│  - MERGE events (merged PRs)                                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Webhook POST /webhook
                             │ (JSON payload)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Flask Application (webhook-repo)                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ POST /webhook                                                │ │
│  │  1. Verify signature                                         │ │
│  │  2. Parse event type (push/pull_request)                     │ │
│  │  3. Extract data (author, branch, timestamp)                 │ │
│  │  4. Store in MongoDB                                         │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ GET /api/events                                              │ │
│  │  1. Query MongoDB                                            │ │
│  │  2. Return events sorted by timestamp                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ GET /                                                        │ │
│  │  Serve HTML/CSS/JS UI                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Store/Retrieve
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          MongoDB Database                           │
│                                                                     │
│  Collection: events                                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ {                                                           │  │
│  │   "_id": ObjectId("..."),                                   │  │
│  │   "request_id": "abc123",                                   │  │
│  │   "author": "Travis",                                       │  │
│  │   "action": "PUSH",                                         │  │
│  │   "from_branch": "main",                                    │  │
│  │   "to_branch": "main",                                      │  │
│  │   "timestamp": "2021-04-01T21:30:00Z"                       │  │
│  │ }                                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Poll every 15 seconds
                             │ GET /api/events
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Web Browser (UI)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  GitHub Webhook Monitor                                      │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │                                                              │ │
│  │  🟢 Live Monitoring (Updates every 15s)                      │ │
│  │                                                              │ │
│  │  Recent Events                               3 events       │ │
│  │  ──────────────────────────────────────────────────────────│ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐│ │
│  │  │ PUSH                      1st Apr 2021 - 9:30 PM UTC   ││ │
│  │  │ Author: Travis                                          ││ │
│  │  │ Request ID: abc123                                      ││ │
│  │  │ Branch: main → main                                     ││ │
│  │  └────────────────────────────────────────────────────────┘│ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐│ │
│  │  │ PULL_REQUEST              1st Apr 2021 - 9:00 AM UTC   ││ │
│  │  │ Author: Travis                                          ││ │
│  │  │ Request ID: 1                                           ││ │
│  │  │ Branch: staging → master                                ││ │
│  │  └────────────────────────────────────────────────────────┘│ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────────┐│ │
│  │  │ MERGE                     2nd Apr 2021 - 12:00 PM UTC  ││ │
│  │  │ Author: Travis                                          ││ │
│  │  │ Request ID: 1                                           ││ │
│  │  │ Branch: dev → master                                    ││ │
│  │  └────────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  JavaScript polls /api/events every 15 seconds                     │
│  Displays new events without duplicates                            │
└─────────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

### 1. Webhook Trigger
```
Developer pushes code to action-repo
    ↓
GitHub detects push event
    ↓
GitHub sends POST request to webhook URL
    ↓
Flask app receives webhook
```

### 2. Data Processing
```
Flask receives GitHub webhook
    ↓
Verify webhook signature (security)
    ↓
Parse event type (push/pull_request)
    ↓
Extract relevant data:
  - Author name
  - Branch names
  - Commit hash / PR number
  - Timestamp
    ↓
Store in MongoDB events collection
    ↓
Return success response to GitHub
```

### 3. UI Update
```
Browser loads page
    ↓
JavaScript fetches /api/events
    ↓
Flask queries MongoDB
    ↓
Returns events as JSON
    ↓
JavaScript renders events in UI
    ↓
Wait 15 seconds
    ↓
Repeat (polling loop)
```

## 🔐 Security Flow

```
1. GitHub generates webhook payload
   ↓
2. GitHub signs payload with secret
   ↓
3. GitHub sends payload + signature
   ↓
4. Flask receives request
   ↓
5. Flask recalculates signature using same secret
   ↓
6. Flask compares signatures
   ↓
7. If match: Process webhook ✅
   If no match: Reject (401) ❌
```

## 📦 File Structure

### webhook-repo
```
webhook-repo/
├── app.py                    # Main Flask application
│   ├── verify_signature()   # Security verification
│   ├── parse_push_event()   # Parse PUSH events
│   ├── parse_pull_request_event()
│   ├── parse_merge_event()
│   └── API routes
├── templates/
│   └── index.html           # UI with JavaScript
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .gitignore              # Git ignore rules
├── Procfile                # Heroku config
├── runtime.txt             # Python version
└── README.md               # Documentation
```

### action-repo
```
action-repo/
├── README.md               # Instructions
├── test.txt               # Test file for commits
└── .gitignore            # Git ignore rules
```

## 🎯 Event Type Mapping

| GitHub Event | Action | Our Mapping | Notes |
|--------------|--------|-------------|-------|
| `push` | N/A | PUSH | Triggered on git push |
| `pull_request` | `opened` | PULL_REQUEST | PR created |
| `pull_request` | `reopened` | PULL_REQUEST | PR reopened |
| `pull_request` | `closed` + `merged=true` | MERGE | PR merged (brownie points!) |

## 🔄 Polling Strategy

```javascript
// Initial load
fetchEvents() {
  displayedEvents = Set()
  fetch all events
  display all events
  add to displayedEvents
}

// Subsequent polls (every 15s)
fetchEvents() {
  fetch all events
  filter out events in displayedEvents
  prepend only new events to UI
  add new events to displayedEvents
}
```

This prevents:
- Duplicate events on refresh
- Full page reload
- Flickering UI

## 🌍 Deployment Architecture

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   GitHub     │       │   Heroku     │       │   MongoDB    │
│  (action-    │──────▶│  (Flask      │◀─────▶│   Atlas      │
│   repo)      │webhook│   app)       │store  │  (Database)  │
└──────────────┘       └──────────────┘       └──────────────┘
                              │
                              │ serve
                              ▼
                       ┌──────────────┐
                       │   Browser    │
                       │   (User UI)  │
                       └──────────────┘
```

## 🚦 Response Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | Success | Event processed successfully |
| 401 | Unauthorized | Invalid webhook signature |
| 400 | Bad Request | No payload or invalid data |
| 500 | Server Error | MongoDB or internal error |

## 📈 Scalability Considerations

Current implementation:
- ✅ Simple polling (15s interval)
- ✅ No authentication needed
- ✅ Single MongoDB collection
- ✅ Suitable for assignment scope

Production improvements (not needed for assignment):
- WebSocket for real-time updates
- Event pagination
- User authentication
- Rate limiting
- Caching layer
- Horizontal scaling

## 🧪 Testing Flow

```
1. Local Testing
   Run Flask app locally
   Use ngrok to expose
   Configure GitHub webhook
   Test all event types
   
2. Deployment
   Deploy to Heroku/Railway/Render
   Update webhook URL in GitHub
   Test with real GitHub events
   
3. Verification
   Check GitHub webhook delivery logs
   Verify MongoDB has events
   Check UI displays correctly
   Confirm 15s auto-refresh works
```

## ✨ Key Features

1. **Webhook Security**
   - HMAC SHA256 signature verification
   - Environment-based secrets

2. **Data Integrity**
   - Proper timestamp handling (UTC)
   - Unique event identification
   - Schema validation

3. **User Experience**
   - Clean, minimal design
   - Real-time updates
   - No duplicate display
   - Responsive layout

4. **Code Quality**
   - Modular functions
   - Comprehensive logging
   - Error handling
   - Documentation

5. **Production Ready**
   - Gunicorn server
   - Health check endpoint
   - Environment configuration
   - Deployment configs

---

This architecture ensures:
- ✅ Reliable webhook processing
- ✅ Secure data handling
- ✅ Clean user interface
- ✅ Production-ready code
- ✅ Easy to deploy and test
