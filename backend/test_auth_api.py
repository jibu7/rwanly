#!/usr/bin/env python3
"""
Simple test script to check auth API permission mapping
"""
import requests
import json
import sys

def test_auth_permissions():
    """Test the auth API permission mapping"""
    # Login to get access token
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    try:
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("Error: No access token returned")
            return
            
        # Get user profile with permissions
        headers = {"Authorization": f"Bearer {access_token}"}
        me_url = "http://localhost:8000/api/auth/me"
        
        me_response = requests.get(me_url, headers=headers)
        me_response.raise_for_status()
        
        user_data = me_response.json()
        
        # Print user data in a formatted way
        print(f"Username: {user_data.get('username')}")
        print(f"Role: {user_data.get('role')}")
        
        # Check permissions
        permissions = user_data.get("permissions", [])
        permission_strings = user_data.get("permission_strings", [])
        
        print(f"\nTotal frontend permissions: {len(permissions)}")
        print(f"Total permission strings: {len(permission_strings)}")
        
        # Check for inventory permissions
        inventory_perms = [p for p in permissions if p.get("resource") == "inventory"]
        inventory_strings = [p for p in permission_strings if "inventory" in p]
        
        print(f"\nInventory frontend permissions: {len(inventory_perms)}")
        print("Inventory permissions:")
        for p in inventory_perms:
            print(f"  - {json.dumps(p)}")
            
        print(f"\nInventory permission strings: {len(inventory_strings)}")
        print("Inventory permission strings:")
        for p in inventory_strings[:10]:  # Show first 10 only
            print(f"  - {p}")
            
        # Check specifically for inventory read permission
        has_inventory_read = any(
            p.get("resource") == "inventory" and p.get("action") == "read"
            for p in permissions
        )
        print(f"\nHas inventory:read frontend permission: {has_inventory_read}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return

if __name__ == "__main__":
    test_auth_permissions()
