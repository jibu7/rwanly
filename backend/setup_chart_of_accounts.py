"""
Sample Chart of Accounts Setup Script
This script creates a basic chart of accounts for a small business
"""

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.core import Company, GLAccount
from app.schemas.core import GLAccountCreate
from app.crud.general_ledger import gl_account_crud


def create_sample_chart_of_accounts(company_id: int, db: Session):
    """Create a sample chart of accounts for a company"""
    
    sample_accounts = [
        # ASSETS
        {
            "account_code": "1000",
            "account_name": "Cash and Cash Equivalents",
            "account_type": "ASSETS",
            "account_subtype": "Current Assets",
            "normal_balance": "DEBIT",
            "description": "Cash, checking, savings accounts"
        },
        {
            "account_code": "1100",
            "account_name": "Accounts Receivable",
            "account_type": "ASSETS",
            "account_subtype": "Current Assets",
            "normal_balance": "DEBIT",
            "description": "Amounts owed by customers"
        },
        {
            "account_code": "1200",
            "account_name": "Inventory",
            "account_type": "ASSETS",
            "account_subtype": "Current Assets",
            "normal_balance": "DEBIT",
            "description": "Products held for sale"
        },
        {
            "account_code": "1300",
            "account_name": "Prepaid Expenses",
            "account_type": "ASSETS",
            "account_subtype": "Current Assets",
            "normal_balance": "DEBIT",
            "description": "Expenses paid in advance"
        },
        {
            "account_code": "1500",
            "account_name": "Equipment",
            "account_type": "ASSETS",
            "account_subtype": "Fixed Assets",
            "normal_balance": "DEBIT",
            "description": "Equipment and machinery"
        },
        {
            "account_code": "1510",
            "account_name": "Accumulated Depreciation - Equipment",
            "account_type": "ASSETS",
            "account_subtype": "Fixed Assets",
            "normal_balance": "CREDIT",
            "description": "Contra asset account for equipment depreciation"
        },
        
        # LIABILITIES
        {
            "account_code": "2000",
            "account_name": "Accounts Payable",
            "account_type": "LIABILITIES",
            "account_subtype": "Current Liabilities",
            "normal_balance": "CREDIT",
            "description": "Amounts owed to suppliers"
        },
        {
            "account_code": "2100",
            "account_name": "Accrued Expenses",
            "account_type": "LIABILITIES",
            "account_subtype": "Current Liabilities",
            "normal_balance": "CREDIT",
            "description": "Expenses incurred but not yet paid"
        },
        {
            "account_code": "2200",
            "account_name": "Sales Tax Payable",
            "account_type": "LIABILITIES",
            "account_subtype": "Current Liabilities",
            "normal_balance": "CREDIT",
            "description": "Sales tax collected from customers"
        },
        {
            "account_code": "2500",
            "account_name": "Long-term Debt",
            "account_type": "LIABILITIES",
            "account_subtype": "Long-term Liabilities",
            "normal_balance": "CREDIT",
            "description": "Debt payable beyond one year"
        },
        
        # EQUITY
        {
            "account_code": "3000",
            "account_name": "Owner's Equity",
            "account_type": "EQUITY",
            "account_subtype": "Capital",
            "normal_balance": "CREDIT",
            "description": "Owner's investment in the business"
        },
        {
            "account_code": "3100",
            "account_name": "Retained Earnings",
            "account_type": "EQUITY",
            "account_subtype": "Retained Earnings",
            "normal_balance": "CREDIT",
            "description": "Accumulated profits retained in business"
        },
        
        # REVENUE
        {
            "account_code": "4000",
            "account_name": "Sales Revenue",
            "account_type": "REVENUE",
            "account_subtype": "Operating Revenue",
            "normal_balance": "CREDIT",
            "description": "Revenue from primary business activities"
        },
        {
            "account_code": "4100",
            "account_name": "Service Revenue",
            "account_type": "REVENUE",
            "account_subtype": "Operating Revenue",
            "normal_balance": "CREDIT",
            "description": "Revenue from services provided"
        },
        {
            "account_code": "4500",
            "account_name": "Interest Income",
            "account_type": "REVENUE",
            "account_subtype": "Other Revenue",
            "normal_balance": "CREDIT",
            "description": "Income from interest earned"
        },
        
        # EXPENSES
        {
            "account_code": "5000",
            "account_name": "Cost of Goods Sold",
            "account_type": "EXPENSES",
            "account_subtype": "Cost of Sales",
            "normal_balance": "DEBIT",
            "description": "Direct costs of products sold"
        },
        {
            "account_code": "6000",
            "account_name": "Salaries and Wages",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Employee compensation"
        },
        {
            "account_code": "6100",
            "account_name": "Rent Expense",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Rent for office or facility"
        },
        {
            "account_code": "6200",
            "account_name": "Utilities Expense",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Electricity, water, gas, internet"
        },
        {
            "account_code": "6300",
            "account_name": "Office Supplies Expense",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Office supplies and materials"
        },
        {
            "account_code": "6400",
            "account_name": "Marketing and Advertising",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Marketing and promotional expenses"
        },
        {
            "account_code": "6500",
            "account_name": "Depreciation Expense",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Depreciation of fixed assets"
        },
        {
            "account_code": "6600",
            "account_name": "Insurance Expense",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Business insurance premiums"
        },
        {
            "account_code": "6700",
            "account_name": "Professional Services",
            "account_type": "EXPENSES",
            "account_subtype": "Operating Expenses",
            "normal_balance": "DEBIT",
            "description": "Legal, accounting, consulting fees"
        },
        {
            "account_code": "7000",
            "account_name": "Interest Expense",
            "account_type": "EXPENSES",
            "account_subtype": "Other Expenses",
            "normal_balance": "DEBIT",
            "description": "Interest paid on loans and debt"
        }
    ]
    
    created_accounts = []
    
    for account_data in sample_accounts:
        # Check if account already exists
        existing_account = gl_account_crud.get_account_by_code(
            db, account_data["account_code"], company_id
        )
        
        if not existing_account:
            account_create = GLAccountCreate(
                company_id=company_id,
                **account_data
            )
            
            try:
                account = gl_account_crud.create_account(db, account_create)
                created_accounts.append(account)
                print(f"Created account: {account.account_code} - {account.account_name}")
            except Exception as e:
                print(f"Error creating account {account_data['account_code']}: {e}")
        else:
            print(f"Account {account_data['account_code']} already exists, skipping...")
    
    print(f"\nChart of accounts setup complete. Created {len(created_accounts)} accounts.")
    return created_accounts


if __name__ == "__main__":
    # This script can be run standalone to setup sample chart of accounts
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python setup_chart_of_accounts.py <company_id>")
        sys.exit(1)
    
    try:
        company_id = int(sys.argv[1])
    except ValueError:
        print("Error: company_id must be an integer")
        sys.exit(1)
    
    # Get database session
    db = next(get_db())
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        print(f"Error: Company with ID {company_id} not found")
        sys.exit(1)
    
    print(f"Setting up chart of accounts for company: {company.name}")
    create_sample_chart_of_accounts(company_id, db)
