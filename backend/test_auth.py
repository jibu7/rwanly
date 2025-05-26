#!/usr/bin/env python3
"""
Test authentication and GL endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api"

def test_login():
    """Test login functionality"""
    # First create a user manually via database
    from app.database.database import SessionLocal
    from app.models.core import Company, User, Role, UserRole
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        # Create company if not exists
        company = db.query(Company).filter(Company.name == "Test Company").first()
        if not company:
            company = Company(
                name="Test Company",
                address={"street": "123 Test St", "city": "Test City", "country": "Test Country"},
                contact_info={"email": "test@test.com"},
                settings={"default_currency": "USD"}
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        # Create role if not exists  
        role = db.query(Role).filter(Role.name == "admin").first()
        if not role:
            role = Role(
                name="admin",
                display_name="Administrator", 
                description="Full access",
                permissions=["gl:*", "sys:*"]
            )
            db.add(role)
            db.commit()
            db.refresh(role)
        
        # Create user if not exists
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                email="test@test.com",
                first_name="Test",
                last_name="User", 
                password_hash=get_password_hash("testpass"),
                company_id=company.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Assign role
            user_role = UserRole(user_id=user.id, role_id=role.id)
            db.add(user_role)
            db.commit()
        
        print(f"Test user created: testuser/testpass (Company ID: {company.id})")
        return company.id
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def get_token():
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "testuser",
                "password": "testpass"
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("Login successful!")
            return token_data.get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_gl_endpoints(token):
    """Test GL endpoints with authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing GL Endpoints ===")
    
    # Test GET /gl/accounts
    try:
        response = requests.get(f"{BASE_URL}/gl/accounts", headers=headers)
        print(f"GET /gl/accounts: {response.status_code}")
        if response.status_code == 200:
            accounts = response.json()
            print(f"Found {len(accounts)} accounts")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing accounts: {e}")
    
    # Test GET /gl/trial-balance
    try:
        response = requests.get(f"{BASE_URL}/gl/trial-balance", headers=headers)
        print(f"GET /gl/trial-balance: {response.status_code}")
        if response.status_code == 200:
            trial_balance = response.json()
            print(f"Trial balance has {len(trial_balance)} entries")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing trial balance: {e}")

def main():
    print("Setting up test environment...")
    
    # Create test user and company
    company_id = test_login()
    if not company_id:
        print("Failed to create test user")
        return
    
    # Get authentication token
    token = get_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    # Test GL endpoints
    test_gl_endpoints(token)
    
    print("\n✅ GL API testing complete!")

if __name__ == "__main__":
    main()
