#!/usr/bin/env python3
"""
Create a test user for testing the API
"""

from app.database.database import SessionLocal
from app.models import Company, User, Role, UserRole
from app.core.security import get_password_hash
from app.core.permissions import DEFAULT_ROLES

def create_test_data():
    """Create test company, roles, and user"""
    db = SessionLocal()
    
    try:
        # Create test company first
        print("Creating test company...")
        company = Company(
            name="Test Company Ltd",
            address={
                "street": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "12345",
                "country": "Test Country"
            },
            contact_info={
                "phone": "+1-555-0123",
                "email": "info@testcompany.com",
                "website": "www.testcompany.com"
            },
            settings={
                "default_currency": "USD",
                "date_format": "YYYY-MM-DD",
                "financial_year_start": "01-01"
            }
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"✅ Created company: {company.name} (ID: {company.id})")
        
        # Create default roles for this company
        print("Creating default roles...")
        created_roles = {}
        
        for role_name, permissions in DEFAULT_ROLES.items():
            role = Role(
                name=role_name,
                description=f"Default {role_name} role",
                permissions=permissions,
                company_id=company.id  # Set the company_id
            )
            db.add(role)
            db.commit()
            db.refresh(role)
            created_roles[role_name] = role
            print(f"✅ Created role: {role_name}")
        
        # Create test user
        print("Creating test user...")
        user = User(
            username="admin@testcompany.com", # Changed from "admin"
            email="admin@testcompany.com",
            first_name="Test",
            last_name="Admin",
            password_hash=get_password_hash("admin123"),
            is_active=True,
            company_id=company.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created user: {user.email} (ID: {user.id})")
        
        # Assign Accountant role to user
        print("Assigning role to user...")
        user_role = UserRole(
            user_id=user.id,
            role_id=created_roles["Accountant"].id
        )
        db.add(user_role)
        db.commit()
        print("✅ Assigned Accountant role to user")
        
        print("\n🎉 Test data created successfully!")
        print(f"Login credentials:")
        print(f"  Email: admin@testcompany.com")
        print(f"  Password: admin123")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
