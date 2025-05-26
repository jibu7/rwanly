#!/usr/bin/env python3
"""
Setup additional AR-specific GL accounts
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.models.core import GLAccount, Company

def setup_ar_accounts():
    """Create additional AR-specific GL accounts"""
    db = SessionLocal()
    try:
        # Get the default company
        company = db.query(Company).first()
        if not company:
            print("Error: No company found. Please set up a company first.")
            return
        
        # AR-related accounts to create
        ar_accounts = [
            {
                "account_code": "1201",
                "account_name": "Trade Receivables",
                "account_type": "Asset",
                "account_subtype": "Current Asset",
                "normal_balance": "Debit",
                "description": "Trade accounts receivable from customers",
                "is_control_account": False
            },
            {
                "account_code": "1202", 
                "account_name": "Other Receivables",
                "account_type": "Asset",
                "account_subtype": "Current Asset", 
                "normal_balance": "Debit",
                "description": "Non-trade receivables",
                "is_control_account": False
            },
            {
                "account_code": "1203",
                "account_name": "Allowance for Doubtful Accounts",
                "account_type": "Asset",
                "account_subtype": "Current Asset",
                "normal_balance": "Credit", 
                "description": "Provision for bad debts",
                "is_control_account": False
            },
            {
                "account_code": "4001",
                "account_name": "Sales Revenue - Products",
                "account_type": "Revenue",
                "account_subtype": "Operating Revenue",
                "normal_balance": "Credit",
                "description": "Revenue from product sales",
                "is_control_account": False
            },
            {
                "account_code": "4002",
                "account_name": "Sales Revenue - Services", 
                "account_type": "Revenue",
                "account_subtype": "Operating Revenue",
                "normal_balance": "Credit",
                "description": "Revenue from service sales",
                "is_control_account": False
            },
            {
                "account_code": "4003",
                "account_name": "Sales Discounts",
                "account_type": "Revenue", 
                "account_subtype": "Operating Revenue",
                "normal_balance": "Debit",
                "description": "Discounts given to customers",
                "is_control_account": False
            },
            {
                "account_code": "4004",
                "account_name": "Sales Returns and Allowances",
                "account_type": "Revenue",
                "account_subtype": "Operating Revenue", 
                "normal_balance": "Debit",
                "description": "Returns and allowances from customers",
                "is_control_account": False
            }
        ]
        
        created_count = 0
        for account_data in ar_accounts:
            # Check if account already exists
            existing = db.query(GLAccount).filter(
                GLAccount.account_code == account_data["account_code"],
                GLAccount.company_id == company.id
            ).first()
            
            if existing:
                print(f"Account {account_data['account_code']} already exists: {existing.account_name}")
                continue
                
            # Create the account
            account = GLAccount(
                company_id=company.id,
                account_code=account_data["account_code"],
                account_name=account_data["account_name"],
                account_type=account_data["account_type"],
                account_subtype=account_data["account_subtype"],
                normal_balance=account_data["normal_balance"],
                description=account_data["description"],
                is_control_account=account_data["is_control_account"],
                is_active=True
            )
            
            db.add(account)
            db.commit()
            db.refresh(account)
            print(f"Created account {account.account_code}: {account.account_name}")
            created_count += 1
        
        print(f"\nSuccessfully created {created_count} new AR accounts")
        
    except Exception as e:
        print(f"Error setting up AR accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_ar_accounts()
