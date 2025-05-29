#!/usr/bin/env python3

import requests
import json
from app.models.core import User
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.database.database import engine

def get_admin_user():
    """Get an admin user for testing"""
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "admin").first()
        return user

def test_inventory_creation():
    """Test inventory item creation"""
    
    # First login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post("http://localhost:8000/api/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test creating an inventory item
    inventory_item = {
        "item_code": "TEST001",
        "description": "Test Inventory Item",
        "item_type": "Stock",
        "unit_of_measure": "EA",
        "cost_price": 10.00,
        "selling_price": 15.00,
        "costing_method": "WeightedAverage",
        "is_active": True
    }
    
    print("Testing inventory item creation...")
    response = requests.post(
        "http://localhost:8000/api/inventory/items",
        headers=headers,
        json=inventory_item
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 201:
        print("✅ Inventory item created successfully!")
        return response.json()
    else:
        print("❌ Failed to create inventory item")
        return None

if __name__ == "__main__":
    result = test_inventory_creation()
    if result:
        print(f"Created item with ID: {result.get('id')}")
