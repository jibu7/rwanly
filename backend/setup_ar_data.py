#!/usr/bin/env python3
"""
Setup AR (Accounts Receivable) default data for rwanly Core ERP
Creates default AR transaction types and ageing periods for all companies.
"""

import sys
import os
from sqlalchemy.orm import Session
from datetime import date

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))

from app.database.database import SessionLocal
from app.models.core import Company, GLAccount, ARTransactionType, AgeingPeriod
from app.crud.accounts_receivable import ageing_period_crud


def setup_ar_transaction_types(db: Session, company_id: int):
    """Setup default AR transaction types for a company"""
    
    # Find required GL accounts
    ar_control_account = db.query(GLAccount).filter(
        GLAccount.company_id == company_id,
        GLAccount.account_type == "Asset",
        GLAccount.account_code.like("12%")  # Typical AR control account
    ).first()
    
    sales_income_account = db.query(GLAccount).filter(
        GLAccount.company_id == company_id,
        GLAccount.account_type == "Revenue",
        GLAccount.account_code.like("40%")  # Typical sales account
    ).first()
    
    if not ar_control_account:
        print(f"Warning: No AR control account found for company {company_id}")
        return
    
    if not sales_income_account:
        print(f"Warning: No sales income account found for company {company_id}")
        return
    
    # Default AR transaction types
    default_types = [
        {
            "type_code": "INV",
            "type_name": "Customer Invoice",
            "description": "Customer invoice for goods or services sold",
            "gl_account_id": ar_control_account.id,
            "default_income_account_id": sales_income_account.id,
            "affects_balance": "DEBIT",
            "is_active": True
        },
        {
            "type_code": "CNO",
            "type_name": "Credit Note", 
            "description": "Credit note to reduce customer balance",
            "gl_account_id": ar_control_account.id,
            "default_income_account_id": sales_income_account.id,
            "affects_balance": "CREDIT",
            "is_active": True
        },
        {
            "type_code": "PMT",
            "type_name": "Customer Payment",
            "description": "Payment received from customer",
            "gl_account_id": ar_control_account.id,
            "default_income_account_id": None,
            "affects_balance": "CREDIT",
            "is_active": True
        },
        {
            "type_code": "ADJ",
            "type_name": "Balance Adjustment",
            "description": "Manual balance adjustment",
            "gl_account_id": ar_control_account.id,
            "default_income_account_id": None,
            "affects_balance": "DEBIT",
            "is_active": True
        }
    ]
    
    created_count = 0
    for type_data in default_types:
        # Check if type already exists
        existing = db.query(ARTransactionType).filter(
            ARTransactionType.company_id == company_id,
            ARTransactionType.type_code == type_data["type_code"]
        ).first()
        
        if not existing:
            ar_type = ARTransactionType(
                company_id=company_id,
                **type_data
            )
            db.add(ar_type)
            created_count += 1
            print(f"Created AR transaction type: {type_data['type_code']} - {type_data['type_name']}")
    
    if created_count > 0:
        db.commit()
        print(f"Successfully created {created_count} AR transaction types for company {company_id}")
    else:
        print(f"AR transaction types already exist for company {company_id}")


def setup_ageing_periods(db: Session, company_id: int):
    """Setup default ageing periods for a company"""
    
    # Check if ageing periods already exist
    existing_periods = db.query(AgeingPeriod).filter(
        AgeingPeriod.company_id == company_id
    ).count()
    
    if existing_periods > 0:
        print(f"Ageing periods already exist for company {company_id}")
        return
    
    # Use the CRUD method to setup default ageing periods
    try:
        periods = ageing_period_crud.setup_default_ageing_periods(db, company_id)
        print(f"Successfully created {len(periods)} default ageing periods for company {company_id}")
        for period in periods:
            print(f"  - {period.period_name}: {period.days_from}-{period.days_to} days")
    except Exception as e:
        print(f"Error creating ageing periods for company {company_id}: {str(e)}")


def main():
    """Main setup function"""
    print("Setting up AR (Accounts Receivable) default data...")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all companies
        companies = db.query(Company).all()
        
        if not companies:
            print("No companies found!")
            return
        
        print(f"Found {len(companies)} companies")
        print()
        
        # Setup AR data for each company
        for company in companies:
            print(f"Setting up AR data for company: {company.name} (ID: {company.id})")
            print("-" * 50)
            
            # Setup AR transaction types
            setup_ar_transaction_types(db, company.id)
            print()
            
            # Setup ageing periods
            setup_ageing_periods(db, company.id)
            print()
        
        print("AR setup completed successfully!")
        
    except Exception as e:
        print(f"Error during AR setup: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
