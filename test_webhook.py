#!/usr/bin/env python3
"""
Quick Test Script for Webhook Receiver
Tests the Flask application endpoints and MongoDB connection
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"  # Change this to your deployed URL

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_webhook_push():
    """Test webhook with a PUSH event"""
    print("\n🔍 Testing PUSH Webhook...")
    
    payload = {
        "ref": "refs/heads/main",
        "after": "abc123def456",
        "pusher": {
            "name": "TestUser"
        },
        "head_commit": {
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_webhook_pull_request():
    """Test webhook with a PULL_REQUEST event"""
    print("\n🔍 Testing PULL_REQUEST Webhook...")
    
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 1,
            "user": {
                "login": "TestUser"
            },
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_webhook_merge():
    """Test webhook with a MERGE event"""
    print("\n🔍 Testing MERGE Webhook (Brownie Points!)...")
    
    payload = {
        "action": "closed",
        "pull_request": {
            "number": 1,
            "merged": True,
            "merged_by": {
                "login": "TestUser"
            },
            "user": {
                "login": "TestUser"
            },
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            },
            "merged_at": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_get_events():
    """Test get events endpoint"""
    print("\n🔍 Testing Get Events Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/events")
        events = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Number of events: {len(events)}")
        
        if events:
            print(f"   Latest event: {events[0]['action']} by {events[0]['author']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_ui():
    """Test UI endpoint"""
    print("\n🔍 Testing UI Endpoint...")
    try:
        response = requests.get(BASE_URL)
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)} bytes")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 GitHub Webhook Receiver Test Suite")
    print("=" * 60)
    print(f"Testing URL: {BASE_URL}")
    
    results = {
        "Health Check": test_health(),
        "UI Endpoint": test_ui(),
        "PUSH Webhook": test_webhook_push(),
        "PULL_REQUEST Webhook": test_webhook_pull_request(),
        "MERGE Webhook": test_webhook_merge(),
        "Get Events API": test_get_events(),
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("\n" + "=" * 60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your application is working correctly.")
        print("Now test with real GitHub webhooks!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Make sure:")
        print("1. Flask application is running")
        print("2. MongoDB is connected")
        print("3. BASE_URL is correct")

if __name__ == "__main__":
    main()
