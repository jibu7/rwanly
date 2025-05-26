#!/usr/bin/env python3
"""
Simple test to create sample data for GL testing
"""
from app.database.database import SessionLocal, engine, Base
from app.models.core import Company, User, Role, GLAccount
from app.core.security import get_password_hash
from app.core.permissions import DEFAULT_ROLES
from datetime import date

def main():
    print("Starting database setup...")
    
    # Create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if sample company exists
        company = db.query(Company).filter(Company.name == "Sample Company Ltd").first()
        if not company:
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
                    "email": "info@samplecompany.com"
                },
                settings={
                    "default_currency": "USD",
                    "date_format": "YYYY-MM-DD"
                }
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"Company created with ID: {company.id}")
        else:
            print(f"Company already exists with ID: {company.id}")
        
        # Create admin role if not exists
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            print("Creating admin role...")
            admin_role = Role(
                name="admin",
                display_name="Administrator",
                description="System administrator with full access",
                permissions=["sys:*", "gl:*"]  # Grant all permissions
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"Admin role created with ID: {admin_role.id}")
        else:
            print(f"Admin role already exists with ID: {admin_role.id}")
            
        # Create admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                username="admin",
                email="admin@samplecompany.com",
                first_name="Admin",
                last_name="User",
                password_hash=get_password_hash("admin123"),
                company_id=company.id,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Admin user created with ID: {admin_user.id}")
            
            # Assign admin role to user
            from app.models.core import UserRole
            user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.add(user_role)
            db.commit()
            print("Admin role assigned to user")
        else:
            print(f"Admin user already exists with ID: {admin_user.id}")
        
        # Create some sample GL accounts
        sample_accounts = [
            {"account_code": "1000", "account_name": "Cash", "account_type": "asset", "normal_balance": "debit"},
            {"account_code": "1200", "account_name": "Accounts Receivable", "account_type": "asset", "normal_balance": "debit"},
            {"account_code": "2000", "account_name": "Accounts Payable", "account_type": "liability", "normal_balance": "credit"},
            {"account_code": "3000", "account_name": "Owner's Equity", "account_type": "equity", "normal_balance": "credit"},
            {"account_code": "4000", "account_name": "Revenue", "account_type": "revenue", "normal_balance": "credit"},
            {"account_code": "5000", "account_name": "Office Expenses", "account_type": "expense", "normal_balance": "debit"},
        ]
        
        for account_data in sample_accounts:
            existing = db.query(GLAccount).filter(
                GLAccount.account_code == account_data["account_code"],
                GLAccount.company_id == company.id
            ).first()
            
            if not existing:
                print(f"Creating GL account: {account_data['account_code']} - {account_data['account_name']}")
                gl_account = GLAccount(
                    company_id=company.id,
                    **account_data
                )
                db.add(gl_account)
        
        db.commit()
        print("Sample GL accounts created!")
        
        print(f"\n✅ Database setup complete!")
        print(f"Company ID: {company.id}")
        print(f"Admin username: admin")
        print(f"Admin password: admin123")
        print(f"You can now test the GL API endpoints!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
