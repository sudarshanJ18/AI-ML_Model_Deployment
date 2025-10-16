#!/usr/bin/env python3
"""
Test script for Real Face Recognition API
"""

import requests
import json
import os
from pathlib import Path

def test_api_endpoints():
    """Test the real face recognition API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Real Face Recognition API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Get faces (should be empty initially)
    print("\n2. Testing get faces endpoint...")
    try:
        response = requests.get(f"{base_url}/faces", timeout=10)
        if response.status_code == 200:
            print("✅ Get faces endpoint working")
            faces = response.json()
            print(f"   Found {len(faces)} faces in database")
        else:
            print(f"❌ Get faces failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Get faces failed: {e}")
    
    # Test 3: Get logs
    print("\n3. Testing get logs endpoint...")
    try:
        response = requests.get(f"{base_url}/logs", timeout=10)
        if response.status_code == 200:
            print("✅ Get logs endpoint working")
            logs = response.json()
            print(f"   Found {len(logs)} logs in database")
        else:
            print(f"❌ Get logs failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Get logs failed: {e}")
    
    # Test 4: Test with a sample image if available
    print("\n4. Testing real face recognition...")
    sample_image_path = Path("test.jpg")
    if sample_image_path.exists():
        try:
            with open(sample_image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{base_url}/recognize", files=files, timeout=30)
            
            if response.status_code == 200:
                print("✅ Real face recognition working")
                result = response.json()
                print(f"   Faces detected: {result.get('faces_detected', 0)}")
                if 'recognized_faces' in result:
                    for i, face in enumerate(result['recognized_faces']):
                        print(f"   Face {i+1}: {face.get('name', 'Unknown')} (confidence: {face.get('confidence', 0):.2f})")
            else:
                print(f"❌ Face recognition failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Face recognition failed: {e}")
    else:
        print("⚠️  No test image found (test.jpg), skipping face recognition test")
        print("   To test face recognition:")
        print("   1. Add a photo named 'test.jpg' to the project root")
        print("   2. Run this test again")
    
    print("\n" + "=" * 50)
    print("🎉 Real API testing completed!")
    return True

def test_frontend():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost:3000")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        print("   Make sure to start the frontend with: npm start")

if __name__ == "__main__":
    print("🚀 Real Face Recognition Application Test Suite")
    print("=" * 60)
    
    # Test backend API
    test_api_endpoints()
    
    # Test frontend
    test_frontend()
    
    print("\n📋 Test Summary:")
    print("- Backend API: Real face detection and recognition")
    print("- Frontend: Check if React app is running on port 3000")
    print("- MongoDB: Persistent storage for faces and logs")
    print("\n💡 To start the application:")
    print("   Windows: Run start_real_app.bat")
    print("   Manual: Start MongoDB, then backend, then frontend")
    print("\n💡 Features:")
    print("- Real face detection using MTCNN")
    print("- Face recognition using FaceNet embeddings")
    print("- MongoDB for persistent storage")
    print("- Live camera recognition")
    print("- Image upload recognition")
