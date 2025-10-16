#!/usr/bin/env python3
"""
Test script for real face recognition functionality
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8001"
TEST_IMAGE_PATH = "test.jpg"  # Use existing test image

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_ready_endpoint():
    """Test the readiness endpoint"""
    print("🔍 Testing readiness endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/ready", timeout=10)
        if response.status_code == 200:
            ready_data = response.json()
            print(f"✅ Readiness check passed: {ready_data}")
            return True
        else:
            print(f"❌ Readiness check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Readiness check error: {e}")
        return False

def test_get_faces():
    """Test getting faces"""
    print("🔍 Testing get faces endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/faces", timeout=10)
        if response.status_code == 200:
            faces_data = response.json()
            print(f"✅ Get faces passed: Found {len(faces_data)} faces")
            return True
        else:
            print(f"❌ Get faces failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get faces error: {e}")
        return False

def test_add_face():
    """Test adding a face"""
    print("🔍 Testing add face endpoint...")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        return False
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': f}
            data = {'name': 'TestPerson'}
            response = requests.post(f"{API_BASE_URL}/faces", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            face_data = response.json()
            print(f"✅ Add face passed: {face_data['message']}")
            return True
        else:
            print(f"❌ Add face failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Add face error: {e}")
        return False

def test_recognize_face():
    """Test face recognition"""
    print("🔍 Testing face recognition endpoint...")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        return False
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': f}
            data = {'threshold': 0.6}
            response = requests.post(f"{API_BASE_URL}/recognize", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            recognition_data = response.json()
            print(f"✅ Face recognition passed: {recognition_data}")
            return True
        else:
            print(f"❌ Face recognition failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Face recognition error: {e}")
        return False

def test_get_logs():
    """Test getting logs"""
    print("🔍 Testing get logs endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/logs", timeout=10)
        if response.status_code == 200:
            logs_data = response.json()
            print(f"✅ Get logs passed: Found {len(logs_data)} logs")
            return True
        else:
            print(f"❌ Get logs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get logs error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 REAL FACE RECOGNITION TEST SUITE")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Readiness Check", test_ready_endpoint),
        ("Get Faces", test_get_faces),
        ("Add Face", test_add_face),
        ("Recognize Face", test_recognize_face),
        ("Get Logs", test_get_logs),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Real face recognition is working!")
    else:
        print("⚠️  Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

