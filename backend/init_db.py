#!/usr/bin/env python3
"""
Initialize the rwanly database with sample data
"""
import sys
import os
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database.database import engine, SessionLocal, Base
from app.models import Base, Company, User, Role, UserRole
from app.core.security import get_password_hash
from app.core.permissions import DEFAULT_ROLES


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def create_sample_company(db: Session):
    """Create a sample company"""
    print("Creating sample company...")
    
    company = Company(
        name="Sample Company Ltd",
        address={
            "street": "123 Business Street",
            "city": "Business City",
            "state": "Business State",
            "zip_code": "12345",
            "country": "Country"
        },
        contact_info={
            "phone": "+1-555-0123",
            "email": "info@samplecompany.com",
            "website": "www.samplecompany.com"
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
    print(f"Sample company created with ID: {company.id}")
    return company


def create_default_roles(db: Session, company_id: int):
    """Create default roles for the company"""
    print("Creating default roles...")
    
    roles = []
    for role_name, permissions in DEFAULT_ROLES.items():
        role = Role(
            name=role_name,
            description=f"Default {role_name} role",
            permissions=permissions,
            company_id=company_id
        )
        db.add(role)
        roles.append(role)
    
    db.commit()
    for role in roles:
        db.refresh(role)
        print(f"Created role: {role.name} with {len(role.permissions)} permissions")
    
    return roles


def create_admin_user(db: Session, company_id: int, admin_role_id: int):
    """Create an admin user"""
    print("Creating admin user...")
    
    admin_user = User(
        username="admin",
        email="admin@samplecompany.com",
        password_hash=get_password_hash("admin123"),  # Change this in production!
        company_id=company_id,
        first_name="System",
        last_name="Administrator",
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # Assign admin role
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role_id)
    db.add(user_role)
    db.commit()
    
    print(f"Admin user created: {admin_user.username}")
    print("Default credentials: admin / admin123")
    print("*** CHANGE THE DEFAULT PASSWORD IN PRODUCTION! ***")
    
    return admin_user


def main():
    """Main initialization function"""
    print("Initializing rwanly Core ERP database...")
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if company already exists
        existing_company = db.query(Company).first()
        if existing_company:
            print("Database already initialized!")
            return
        
        # Create sample company
        company = create_sample_company(db)
        
        # Create default roles
        roles = create_default_roles(db, company.id)
        
        # Find admin role
        admin_role = next((role for role in roles if role.name == "Administrator"), None)
        if not admin_role:
            print("Error: Admin role not created!")
            return
        
        # Create admin user
        create_admin_user(db, company.id, admin_role.id)
        
        print("\n" + "="*50)
        print("Database initialization completed successfully!")
        print("="*50)
        print(f"Company: {company.name}")
        print(f"Admin Username: admin")
        print(f"Admin Password: admin123")
        print("*** CHANGE THE DEFAULT PASSWORD! ***")
        print("="*50)
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
