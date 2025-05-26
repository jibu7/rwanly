#!/usr/bin/env python3
"""
Simple manual test for General Ledger functionality
"""
import requests
import json
from datetime import date

# Base URL for the API
BASE_URL = "http://localhost:8001/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_auth():
    """Test authentication"""
    try:
        # Try to access protected endpoint without auth
        response = requests.get(f"{BASE_URL}/gl/accounts")
        print(f"Unauth GL accounts access: {response.status_code}")
        
        # This should return 401 Unauthorized
        return response.status_code == 401
    except Exception as e:
        print(f"Auth test failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get("http://localhost:8001/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root test failed: {e}")
        return False

def main():
    print("Testing rwanly General Ledger API...")
    print("=" * 50)
    
    tests = [
        ("Root endpoint", test_root),
        ("Health check", test_health), 
        ("Authentication", test_auth),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        if test_func():
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All basic tests passed! Server is running correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main()
