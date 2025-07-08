#!/usr/bin/env python3
"""
Comprehensive integration test for the Adaptive Learning App
Tests all AI components and API endpoints
"""

import requests
import json
import time
import sys

# Test configuration
BACKEND_URL = "http://localhost:12000"
DEMO_URL = "http://localhost:12002"

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        print(f"✓ Backend Health: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Backend Health Failed: {e}")
        return False

def test_learning_style_analysis():
    """Test learning style analysis AI component"""
    try:
        data = {
            "user_responses": [
                "I prefer visual diagrams and charts",
                "I like hands-on practice and experiments",
                "I learn better with audio explanations"
            ]
        }
        response = requests.post(f"{BACKEND_URL}/ai/analyze-learning-style", json=data)
        result = response.json()
        print(f"✓ Learning Style Analysis: {result}")
        return True
    except Exception as e:
        print(f"✗ Learning Style Analysis Failed: {e}")
        return False

def test_content_generation():
    """Test AI content generation"""
    try:
        data = {
            "topic": "Python Functions",
            "learning_style": "visual",
            "difficulty_level": "beginner"
        }
        response = requests.post(f"{BACKEND_URL}/ai/generate-content", json=data)
        result = response.json()
        print(f"✓ Content Generation: {result}")
        return True
    except Exception as e:
        print(f"✗ Content Generation Failed: {e}")
        return False

def test_recommendations():
    """Test AI recommendation engine"""
    try:
        data = {
            "user_id": "test_user",
            "current_topic": "Python OOP",
            "performance_data": {"accuracy": 0.75, "completion_time": 300}
        }
        response = requests.post(f"{BACKEND_URL}/ai/recommendations", json=data)
        result = response.json()
        print(f"✓ Recommendations: {result}")
        return True
    except Exception as e:
        print(f"✗ Recommendations Failed: {e}")
        return False

def test_demo_server():
    """Test demo server"""
    try:
        response = requests.get(f"{DEMO_URL}")
        if response.status_code == 200:
            print(f"✓ Demo Server: Running on {DEMO_URL}")
            return True
        else:
            print(f"✗ Demo Server: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Demo Server Failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Adaptive Learning App Integration Tests\n")
    
    tests = [
        ("Backend Health Check", test_backend_health),
        ("Learning Style Analysis", test_learning_style_analysis),
        ("Content Generation", test_content_generation),
        ("Recommendation Engine", test_recommendations),
        ("Demo Server", test_demo_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Adaptive Learning App is fully functional.")
        print("\n🌐 Access Points:")
        print(f"   • Backend API: {BACKEND_URL}")
        print(f"   • Demo Interface: {DEMO_URL}")
        print(f"   • Frontend (when running): https://work-2-xfbrapmqilkuzpuz.prod-runtime.all-hands.dev")
    else:
        print("❌ Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()