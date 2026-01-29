"""
MongoDB CRUD Operations Test Script
This script tests the basic CRUD operations on the MongoDB database.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables from .env file
load_dotenv()

# MongoDB connection settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'github_webhooks'
COLLECTION_NAME = 'events'

def connect_to_mongodb():
    """Establish connection to MongoDB and return the collection."""
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            connectTimeoutMS=10000,
            socketTimeoutMS=None
        )
        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Use the database name from the environment or default
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        return collection
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def test_crud_operations():
    """Test CRUD operations on the MongoDB collection."""
    collection = connect_to_mongodb()
    if collection is None:
        return

    test_event = {
        'request_id': 'test123',
        'author': 'test_user',
        'action': 'PUSH',
        'from_branch': 'test-branch',
        'to_branch': 'main',
        'timestamp': '2023-01-01T00:00:00Z'
    }

    # Test Create
    print("\n🔹 Testing CREATE operation...")
    try:
        result = collection.insert_one(test_event)
        print(f"✅ Created document with id: {result.inserted_id}")
        test_event_id = str(result.inserted_id)
    except Exception as e:
        print(f"❌ Error creating document: {e}")
        return

    # Test Read
    print("\n🔹 Testing READ operation...")
    try:
        found_event = collection.find_one({'request_id': 'test123'})
        if found_event:
            print("✅ Found document:")
            pprint(found_event)
        else:
            print("❌ Document not found!")
            return
    except Exception as e:
        print(f"❌ Error reading document: {e}")
        return

    # Test Update
    print("\n🔹 Testing UPDATE operation...")
    try:
        update_result = collection.update_one(
            {'request_id': 'test123'},
            {'$set': {'author': 'updated_user'}}
        )
        if update_result.modified_count > 0:
            print("✅ Successfully updated document")
            # Verify the update
            updated_doc = collection.find_one({'request_id': 'test123'})
            print(f"Updated author: {updated_doc['author']}")
        else:
            print("❌ No document was updated")
    except Exception as e:
        print(f"❌ Error updating document: {e}")

    # Test Delete
    print("\n🔹 Testing DELETE operation...")
    try:
        delete_result = collection.delete_one({'request_id': 'test123'})
        if delete_result.deleted_count > 0:
            print("✅ Successfully deleted test document")
        else:
            print("❌ No document was deleted")
    except Exception as e:
        print(f"❌ Error deleting document: {e}")

    # List all documents in the collection
    print("\n📋 Current documents in collection:")
    try:
        count = collection.count_documents({})
        print(f"Total documents: {count}")
        if count > 0:
            print("Sample document:")
            pprint(collection.find_one())
    except Exception as e:
        print(f"❌ Error counting documents: {e}")

if __name__ == "__main__":
    print("🚀 Starting MongoDB CRUD Test...")
    test_crud_operations()
    print("\n✨ CRUD Test Completed!")

# To run this test:
# 1. Make sure your .env file has the correct MONGO_URI
# 2. Install required packages: pip install pymongo python-dotenv
# 3. Run: python test_mongodb.py
