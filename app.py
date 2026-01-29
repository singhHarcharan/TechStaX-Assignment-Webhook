"""
GitHub Webhook Receiver Application
Receives GitHub webhooks for PUSH, PULL_REQUEST, and MERGE actions
and stores them in MongoDB
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
import hashlib
import hmac
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'github_webhooks')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'events')

# GitHub Webhook Secret (optional but recommended for security)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')

# Initialize MongoDB client
try:
    # In app.py, update the MongoDB connection part
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        connectTimeoutMS=30000,
        socketTimeoutMS=None,
        retryWrites=True,
        w='majority'
    )
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise


def verify_signature(payload_body, signature_header):
    """
    Verify that the payload was sent from GitHub by validating the signature.
    """
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret is set
    
    if not signature_header:
        return False
    
    hash_algorithm, github_signature = signature_header.split('=')
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(WEBHOOK_SECRET, 'latin-1')
    mac = hmac.new(encoded_key, msg=payload_body, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


def parse_push_event(payload):
    """
    Parse PUSH event from GitHub webhook payload
    """
    return {
        'request_id': payload.get('after', '')[:7],  # Use commit hash (short)
        'author': payload.get('pusher', {}).get('name', 'Unknown'),
        'action': 'PUSH',
        'from_branch': payload.get('ref', '').replace('refs/heads/', ''),
        'to_branch': payload.get('ref', '').replace('refs/heads/', ''),
        'timestamp': payload.get('head_commit', {}).get('timestamp', 
                                datetime.utcnow().isoformat())
    }


def parse_pull_request_event(payload):
    """
    Parse PULL_REQUEST event from GitHub webhook payload
    """
    pr = payload.get('pull_request', {})
    return {
        'request_id': str(pr.get('number', '')),  # Use PR number
        'author': pr.get('user', {}).get('login', 'Unknown'),
        'action': 'PULL_REQUEST',
        'from_branch': pr.get('head', {}).get('ref', ''),
        'to_branch': pr.get('base', {}).get('ref', ''),
        'timestamp': pr.get('created_at', datetime.utcnow().isoformat())
    }


def parse_merge_event(payload):
    """
    Parse MERGE event (pull_request with merged action) from GitHub webhook payload
    """
    pr = payload.get('pull_request', {})
    return {
        'request_id': str(pr.get('number', '')),
        'author': pr.get('merged_by', {}).get('login', 
                       pr.get('user', {}).get('login', 'Unknown')),
        'action': 'MERGE',
        'from_branch': pr.get('head', {}).get('ref', ''),
        'to_branch': pr.get('base', {}).get('ref', ''),
        'timestamp': pr.get('merged_at', datetime.utcnow().isoformat())
    }


@app.route('/')
def index():
    """
    Render the main UI page
    """
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    GitHub webhook endpoint
    Receives and processes GitHub events
    """
    print("Received headers:", dict(request.headers))
    print("Signature received:", signature)
    print("Expected signature:", generate_signature(request.data))
    try:
        # Verify GitHub signature
        signature = request.headers.get('X-Hub-Signature-256') or \
                   request.headers.get('X-Hub-Signature')
        if not verify_signature(request.data, signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Get event type
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json
        
        if not payload:
            logger.warning("No payload received")
            return jsonify({'error': 'No payload'}), 400
        
        event_data = None
        
        # Parse based on event type
        if event_type == 'push':
            event_data = parse_push_event(payload)
            logger.info(f"Received PUSH event: {event_data['request_id']}")
            
        elif event_type == 'pull_request':
            action = payload.get('action')
            
            if action == 'opened' or action == 'reopened':
                event_data = parse_pull_request_event(payload)
                logger.info(f"Received PULL_REQUEST event: {event_data['request_id']}")
                
            elif action == 'closed' and payload.get('pull_request', {}).get('merged'):
                # This is a merge event (brownie points!)
                event_data = parse_merge_event(payload)
                logger.info(f"Received MERGE event: {event_data['request_id']}")
        
        if event_data:
            # Insert into MongoDB
            result = collection.insert_one(event_data)
            logger.info(f"Stored event in MongoDB with ID: {result.inserted_id}")
            
            return jsonify({
                'status': 'success',
                'message': 'Event processed successfully',
                'id': str(result.inserted_id)
            }), 200
        else:
            logger.info(f"Ignoring event type: {event_type}")
            return jsonify({
                'status': 'ignored',
                'message': 'Event type not processed'
            }), 200
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    API endpoint to fetch all events from MongoDB
    Returns events sorted by timestamp (most recent first)
    """
    try:
        # Fetch events, excluding MongoDB's _id field
        events = list(collection.find(
            {},
            {'_id': 0}
        ).sort('timestamp', -1))
        
        return jsonify(events), 200
    except Exception as e:
        logger.error(f"Error fetching events: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch events'}), 500


@app.route('/api/events/clear', methods=['POST'])
def clear_events():
    """
    API endpoint to clear all events (useful for testing)
    """
    try:
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} events")
        return jsonify({
            'status': 'success',
            'deleted_count': result.deleted_count
        }), 200
    except Exception as e:
        logger.error(f"Error clearing events: {e}", exc_info=True)
        return jsonify({'error': 'Failed to clear events'}), 500


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
