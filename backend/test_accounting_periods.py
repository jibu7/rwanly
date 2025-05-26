#!/usr/bin/env python3
"""
Test the accounting periods API functionality
"""

import requests
import json
from datetime import date, datetime

# Base URL for the API
BASE_URL = "http://localhost:8001"

def test_login():
    """Test user login and get access token"""
    login_data = {
        "username": "admin",  # Use username, not email
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful!")
        return token_data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_accounting_periods(token):
    """Test accounting periods API endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Accounting Periods API ===")
    
    # Test 1: List accounting periods
    print("\n1. Testing list accounting periods...")
    response = requests.get(f"{BASE_URL}/api/accounting-periods/", headers=headers)
    
    if response.status_code == 200:
        periods = response.json()
        print(f"✅ List periods successful! Found {len(periods)} periods")
        for period in periods:
            print(f"   - {period['period_name']}: {period['start_date']} to {period['end_date']} (Status: {period['is_closed']})")
    else:
        print(f"❌ List periods failed: {response.status_code} - {response.text}")
    
    # Test 2: Create a new accounting period
    print("\n2. Testing create accounting period...")
    new_period = {
        "period_name": "Test Period Q4 2025",  # Changed from "name" to "period_name"
        "start_date": "2025-10-01",
        "end_date": "2025-12-31",
        "financial_year": 2025,
        "is_closed": False
        # company_id is set automatically by the API
    }
    
    response = requests.post(f"{BASE_URL}/api/accounting-periods/", 
                           headers=headers, 
                           json=new_period)
    
    if response.status_code == 200:
        created_period = response.json()
        period_id = created_period["id"]
        print(f"✅ Create period successful! ID: {period_id}")
        
        # Test 3: Get the created period
        print("\n3. Testing get specific period...")
        response = requests.get(f"{BASE_URL}/api/accounting-periods/{period_id}", headers=headers)
        
        if response.status_code == 200:
            period = response.json()
            print(f"✅ Get period successful! Period: {period['period_name']}")
        else:
            print(f"❌ Get period failed: {response.status_code} - {response.text}")
        
        # Test 4: Update the period
        print("\n4. Testing update period...")
        update_data = {
            "period_name": "Updated Test Period Q4 2025"  # Changed from "name" to "period_name"
        }
        
        response = requests.put(f"{BASE_URL}/api/accounting-periods/{period_id}", 
                              headers=headers, 
                              json=update_data)
        
        if response.status_code == 200:
            updated_period = response.json()
            print(f"✅ Update period successful! New name: {updated_period['period_name']}")
        else:
            print(f"❌ Update period failed: {response.status_code} - {response.text}")
        
        # Test 5: Close the period
        print("\n5. Testing close period...")
        response = requests.post(f"{BASE_URL}/api/accounting-periods/{period_id}/close", headers=headers)
        
        if response.status_code == 200:
            closed_period = response.json()
            print(f"✅ Close period successful! Status: {closed_period['is_closed']}")
        else:
            print(f"❌ Close period failed: {response.status_code} - {response.text}")
        
        # Test 6: Reopen the period
        print("\n6. Testing reopen period...")
        response = requests.post(f"{BASE_URL}/api/accounting-periods/{period_id}/reopen", headers=headers)
        
        if response.status_code == 200:
            reopened_period = response.json()
            print(f"✅ Reopen period successful! Status: {reopened_period['is_closed']}")
        else:
            print(f"❌ Reopen period failed: {response.status_code} - {response.text}")
        
        # Test 7: Get current period
        print("\n7. Testing get current period...")
        response = requests.get(f"{BASE_URL}/api/accounting-periods/current", headers=headers)
        
        if response.status_code == 200:
            current_period = response.json()
            print(f"✅ Get current period successful! Current: {current_period['period_name']}")
        else:
            print(f"❌ Get current period failed: {response.status_code} - {response.text}")
        
        # Test 8: Get open periods
        print("\n8. Testing get open periods...")
        response = requests.get(f"{BASE_URL}/api/accounting-periods/open", headers=headers)
        
        if response.status_code == 200:
            open_periods = response.json()
            print(f"✅ Get open periods successful! Found {len(open_periods)} open periods")
        else:
            print(f"❌ Get open periods failed: {response.status_code} - {response.text}")
    
    else:
        print(f"❌ Create period failed: {response.status_code} - {response.text}")

def main():
    """Main test function"""
    print("🚀 Starting Accounting Periods API Tests")
    print("=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test accounting periods functionality
    test_accounting_periods(token)
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
