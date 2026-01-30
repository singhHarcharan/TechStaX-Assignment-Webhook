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
import json
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
    """Verify that the payload was sent from GitHub by validating the signature"""
    if not signature_header:
        logger.warning("No signature header")
        return False
    
    try:
        # Get the hash algorithm and signature from the header
        hash_name, signature = signature_header.split('=')
        if hash_name not in ['sha1', 'sha256']:
            logger.warning(f"Unsupported hash algorithm: {hash_name}")
            return False

        # Create a new hash of the payload using the secret
        key = WEBHOOK_SECRET.encode()
        hmac_obj = hmac.new(key, msg=payload_body, digestmod=hash_name)
        expected_signature = hmac_obj.hexdigest()

        # Compare the signatures
        result = hmac.compare_digest(signature, expected_signature)
        if not result:
            logger.warning(f"Signature mismatch. Expected: {expected_signature}, Got: {signature}")
        return result
        
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False


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
    # Get the raw request data first
    request_data = request.get_data()
    
    # Get the signature from headers
    # Get the raw request data first
    request_data = request.get_data()
    
    # Get the signature from headers
    signature = request.headers.get('X-Hub-Signature-256') or \
               request.headers.get('X-Hub-Signature')
    
    # Log the headers and signature for debugging
    logger.debug("Received headers: %s", dict(request.headers))
    logger.debug("Signature received: %s", signature)
    logger.debug("Received headers: %s", dict(request.headers))
    logger.debug("Signature received: %s", signature)
    
    try:
        # Verify GitHub signature with raw request data
        if not verify_signature(request_data, signature):
        # Verify GitHub signature with raw request data
        if not verify_signature(request_data, signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse request data based on content type
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            payload = request.get_json()
        elif 'application/x-www-form-urlencoded' in content_type:
            # For form-encoded data, the payload is in the 'payload' field
            form_data = request.form
            if 'payload' not in form_data:
                logger.warning("No payload in form data")
                return jsonify({'error': 'No payload in form data'}), 400
            try:
                payload = json.loads(form_data['payload'])
            except json.JSONDecodeError:
                logger.error("Invalid JSON in form payload")
                return jsonify({'error': 'Invalid JSON in payload'}), 400
        else:
            logger.warning(f"Unsupported content type: {content_type}")
            return jsonify({'error': 'Unsupported content type'}), 415

        if not payload:
            logger.warning("No payload received")
            return jsonify({'error': 'No payload'}), 400
            
        # Get event type
        event_type = request.headers.get('X-GitHub-Event')
        logger.info(f"Received {event_type} event")
            
        # Get event type
        event_type = request.headers.get('X-GitHub-Event')
        logger.info(f"Received {event_type} event")
        
        # Process different event types
        # Process different event types
        if event_type == 'push':
            event_data = parse_push_event(payload)
        elif event_type == 'pull_request':
            if payload.get('action') == 'closed' and payload.get('pull_request', {}).get('merged'):
                event_data = parse_merge_event(payload)
            else:
            if payload.get('action') == 'closed' and payload.get('pull_request', {}).get('merged'):
                event_data = parse_merge_event(payload)
            else:
                event_data = parse_pull_request_event(payload)
        else:
            logger.warning(f"Unhandled event type: {event_type}")
            return jsonify({'status': 'ignored', 'message': 'Event type not processed'}), 200

        # Store the event in MongoDB
        else:
            logger.warning(f"Unhandled event type: {event_type}")
            return jsonify({'status': 'ignored', 'message': 'Event type not processed'}), 200

        # Store the event in MongoDB
        if event_data:
            event = {
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow(),
                'repository': payload.get('repository', {}).get('full_name', 'unknown'),
                'sender': payload.get('sender', {}).get('login', 'unknown')
            }
            events_collection.insert_one(event)
            logger.info(f"Stored {event_type} event in database")
        
        return jsonify({'status': 'success'}), 200

            event = {
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow(),
                'repository': payload.get('repository', {}).get('full_name', 'unknown'),
                'sender': payload.get('sender', {}).get('login', 'unknown')
            }
            events_collection.insert_one(event)
            logger.info(f"Stored {event_type} event in database")
        
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
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
