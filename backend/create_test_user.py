#!/usr/bin/env python3
"""
Comprehensive Test Data Creation Script for rwanly ERP
Creates a complete test environment with sample data across all modules

🔑 Login Credentials:
Administrator: admin@techflow.com / admin123
Accountant: accountant@techflow.com / accountant123
Sales: sales@techflow.com / sales123
Clerk: clerk@techflow.com / clerk123

Test Data Includes:
- 8 AR transactions (5 invoices + 3 payments)
- 4 AP transactions (bills)
- 5 inventory transactions (3 receipts + 2 issues)
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database.database import SessionLocal
from app.models.core import (
    Company, User, Role, UserRole, AccountingPeriod,
    GLAccount, GLTransaction,
    Customer, ARTransactionType, ARTransaction, ARAllocation, AgeingPeriod,
    Supplier, APTransactionType, APTransaction, APAllocation,
    InventoryItem, InventoryTransactionType, InventoryTransaction
)
from app.core.security import get_password_hash
from app.core.permissions import DEFAULT_ROLES


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"🔄 {title}")
    print('=' * 60)


def create_test_company(db):
    """Create a comprehensive test company with full settings"""
    print("Creating Test Company...")
    
    company = Company(
        name="TechFlow Solutions Ltd",
        address={
            "street": "456 Innovation Boulevard",
            "suite": "Suite 300",
            "city": "Silicon Valley",
            "state": "California",
            "zip_code": "94025",
            "country": "United States"
        },
        contact_info={
            "phone": "+1-650-555-0199",
            "fax": "+1-650-555-0198",
            "email": "info@techflowsolutions.com",
            "website": "www.techflowsolutions.com",
            "tax_id": "XX-1234567"
        },
        settings={
            "default_currency": "USD",
            "date_format": "MM/DD/YYYY",
            "financial_year_start": "01-01",
            "decimal_places": 2,
            "timezone": "America/Los_Angeles",
            "invoice_terms": "Net 30",
            "auto_number_invoices": True,
            "auto_number_orders": True
        }
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    print(f"✅ Created company: {company.name} (ID: {company.id})")
    return company


def create_roles_and_users(db, company_id):
    """Create roles and comprehensive test users"""
    print("Creating Roles and Users...")
    
    # Create default roles
    created_roles = {}
    for role_name, permissions in DEFAULT_ROLES.items():
        role = Role(
            name=role_name,
            description=f"Default {role_name} role with comprehensive permissions",
            permissions=permissions,
            company_id=company_id
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        created_roles[role_name] = role
        print(f"✅ Created role: {role_name}")
    
    # Create comprehensive test users
    test_users = [
        {
            "username": "admin@techflow.com",
            "email": "admin@techflow.com",
            "first_name": "System",
            "last_name": "Administrator",
            "password": "admin123",
            "role": "Administrator"
        },
        {
            "username": "accountant@techflow.com",
            "email": "accountant@techflow.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "password": "accountant123",
            "role": "Accountant"
        },
        {
            "username": "sales@techflow.com",
            "email": "sales@techflow.com",
            "first_name": "Michael",
            "last_name": "Chen",
            "password": "sales123",
            "role": "Sales"
        },
        {
            "username": "clerk@techflow.com",
            "email": "clerk@techflow.com",
            "first_name": "Jennifer",
            "last_name": "Williams",
            "password": "clerk123",
            "role": "Clerk"
        }
    ]
    
    created_users = {}
    for user_data in test_users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            password_hash=get_password_hash(user_data["password"]),
            is_active=True,
            company_id=company_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=created_roles[user_data["role"]].id
        )
        db.add(user_role)
        db.commit()
        
        created_users[user_data["role"]] = user
        print(f"✅ Created user: {user.email} ({user_data['role']})")
    
    return created_users


def create_accounting_periods(db, company_id):
    """Create accounting periods for current and previous years"""
    print("Creating Accounting Periods...")
    
    current_year = datetime.now().year
    periods = []
    
    # Create periods for last year and this year
    for year in [current_year - 1, current_year]:
        for month in range(1, 13):
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            period = AccountingPeriod(
                company_id=company_id,
                period_name=f"{year}-{month:02d}",
                start_date=start_date,
                end_date=end_date,
                financial_year=year,
                is_closed=year < current_year or (year == current_year and month < datetime.now().month)
            )
            db.add(period)
            periods.append(period)
    
    db.commit()
    print(f"✅ Created {len(periods)} accounting periods for {current_year-1}-{current_year}")
    return periods


def create_chart_of_accounts(db, company_id):
    """Create a comprehensive chart of accounts"""
    print("Creating Chart of Accounts...")
    
    accounts_data = [
        # ASSETS
        {"code": "1000", "name": "Cash in Bank - Operating", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1010", "name": "Cash in Bank - Savings", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1020", "name": "Petty Cash", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1100", "name": "Accounts Receivable", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT", "control": True},
        {"code": "1200", "name": "Inventory - Raw Materials", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1210", "name": "Inventory - Work in Progress", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1220", "name": "Inventory - Finished Goods", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1300", "name": "Prepaid Insurance", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1310", "name": "Prepaid Rent", "type": "ASSETS", "subtype": "Current Assets", "balance": "DEBIT"},
        {"code": "1500", "name": "Office Equipment", "type": "ASSETS", "subtype": "Fixed Assets", "balance": "DEBIT"},
        {"code": "1510", "name": "Computer Equipment", "type": "ASSETS", "subtype": "Fixed Assets", "balance": "DEBIT"},
        {"code": "1520", "name": "Furniture & Fixtures", "type": "ASSETS", "subtype": "Fixed Assets", "balance": "DEBIT"},
        {"code": "1600", "name": "Accumulated Depreciation - Equipment", "type": "ASSETS", "subtype": "Fixed Assets", "balance": "CREDIT"},
        
        # LIABILITIES
        {"code": "2000", "name": "Accounts Payable", "type": "LIABILITIES", "subtype": "Current Liabilities", "balance": "CREDIT", "control": True},
        {"code": "2100", "name": "Sales Tax Payable", "type": "LIABILITIES", "subtype": "Current Liabilities", "balance": "CREDIT"},
        {"code": "2110", "name": "Payroll Tax Payable", "type": "LIABILITIES", "subtype": "Current Liabilities", "balance": "CREDIT"},
        {"code": "2200", "name": "Accrued Expenses", "type": "LIABILITIES", "subtype": "Current Liabilities", "balance": "CREDIT"},
        {"code": "2300", "name": "Notes Payable - Short Term", "type": "LIABILITIES", "subtype": "Current Liabilities", "balance": "CREDIT"},
        {"code": "2500", "name": "Long Term Debt", "type": "LIABILITIES", "subtype": "Long Term Liabilities", "balance": "CREDIT"},
        
        # EQUITY
        {"code": "3000", "name": "Owner's Capital", "type": "EQUITY", "subtype": "Owner's Equity", "balance": "CREDIT"},
        {"code": "3100", "name": "Retained Earnings", "type": "EQUITY", "subtype": "Owner's Equity", "balance": "CREDIT"},
        {"code": "3200", "name": "Current Year Earnings", "type": "EQUITY", "subtype": "Owner's Equity", "balance": "CREDIT"},
        
        # REVENUE
        {"code": "4000", "name": "Sales Revenue - Products", "type": "REVENUE", "subtype": "Operating Revenue", "balance": "CREDIT"},
        {"code": "4100", "name": "Sales Revenue - Services", "type": "REVENUE", "subtype": "Operating Revenue", "balance": "CREDIT"},
        {"code": "4200", "name": "Interest Income", "type": "REVENUE", "subtype": "Non-Operating Revenue", "balance": "CREDIT"},
        {"code": "4300", "name": "Other Income", "type": "REVENUE", "subtype": "Non-Operating Revenue", "balance": "CREDIT"},
        
        # EXPENSES
        {"code": "5000", "name": "Cost of Goods Sold", "type": "EXPENSES", "subtype": "Cost of Sales", "balance": "DEBIT"},
        {"code": "6000", "name": "Salaries & Wages", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6100", "name": "Rent Expense", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6200", "name": "Utilities Expense", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6300", "name": "Insurance Expense", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6400", "name": "Professional Services", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6500", "name": "Office Supplies", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6600", "name": "Marketing & Advertising", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6700", "name": "Travel & Entertainment", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "6800", "name": "Depreciation Expense", "type": "EXPENSES", "subtype": "Operating Expenses", "balance": "DEBIT"},
        {"code": "7000", "name": "Interest Expense", "type": "EXPENSES", "subtype": "Non-Operating Expenses", "balance": "DEBIT"},
        {"code": "7100", "name": "Bank Fees", "type": "EXPENSES", "subtype": "Non-Operating Expenses", "balance": "DEBIT"},
    ]
    
    accounts = {}
    for acc_data in accounts_data:
        account = GLAccount(
            company_id=company_id,
            account_code=acc_data["code"],
            account_name=acc_data["name"],
            account_type=acc_data["type"],
            account_subtype=acc_data["subtype"],
            normal_balance=acc_data["balance"],
            is_active=True,
            is_control_account=acc_data.get("control", False),
            description=f"{acc_data['subtype']} account for {acc_data['name'].lower()}"
        )
        db.add(account)
        accounts[acc_data["code"]] = account
    
    db.commit()
    print(f"✅ Created {len(accounts)} GL accounts")
    return accounts


def create_customers(db, company_id):
    """Create comprehensive customer data"""
    print("Creating Customers...")
    
    customers_data = [
        {
            "code": "CUST001",
            "name": "Acme Corporation",
            "contact": "John Smith",
            "email": "john.smith@acmecorp.com",
            "phone": "+1-555-0101",
            "address": "123 Business Ave, Suite 100",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105",
            "terms": 30,
            "credit_limit": 50000.00
        },
        {
            "code": "CUST002", 
            "name": "TechStart Inc",
            "contact": "Sarah Davis",
            "email": "sarah@techstart.com",
            "phone": "+1-555-0102",
            "address": "456 Innovation St",
            "city": "Palo Alto",
            "state": "CA", 
            "zip": "94301",
            "terms": 15,
            "credit_limit": 25000.00
        },
        {
            "code": "CUST003",
            "name": "Global Manufacturing Ltd",
            "contact": "Robert Wilson",
            "email": "r.wilson@globalmfg.com",
            "phone": "+1-555-0103",
            "address": "789 Industrial Blvd",
            "city": "San Jose",
            "state": "CA",
            "zip": "95113", 
            "terms": 45,
            "credit_limit": 100000.00
        }
    ]
    
    customers = {}
    for cust_data in customers_data:
        customer = Customer(
            company_id=company_id,
            customer_code=cust_data["code"],
            name=cust_data["name"],
            contact_person=cust_data["contact"],
            email=cust_data["email"],
            phone=cust_data["phone"],
            address_line1=cust_data["address"],
            city=cust_data["city"],
            state=cust_data["state"],
            postal_code=cust_data["zip"],
            country="USA",
            payment_terms_days=cust_data["terms"],
            credit_limit=Decimal(str(cust_data["credit_limit"])),
            current_balance=Decimal('0.00'),
            is_active=True
        )
        db.add(customer)
        customers[cust_data["code"]] = customer
    
    db.commit()
    print(f"✅ Created {len(customers)} customers")
    return customers


def create_suppliers(db, company_id):
    """Create comprehensive supplier data"""
    print("Creating Suppliers...")
    
    suppliers_data = [
        {
            "code": "SUPP001",
            "name": "TechParts Supply Co",
            "contact": "James Miller",
            "email": "james@techparts.com",
            "phone": "+1-555-0201",
            "address": "100 Supplier St",
            "city": "Oakland",
            "state": "CA",
            "zip": "94607",
            "terms": 30,
            "credit_limit": 25000.00
        },
        {
            "code": "SUPP002",
            "name": "Office Depot Business",
            "contact": "Lisa Anderson",
            "email": "lisa@officedepot.com", 
            "phone": "+1-555-0202",
            "address": "200 Office Way",
            "city": "Fremont",
            "state": "CA",
            "zip": "94536",
            "terms": 15,
            "credit_limit": 10000.00
        },
        {
            "code": "SUPP003",
            "name": "Industrial Materials Inc",
            "contact": "Mark Thompson",
            "email": "mark@indmaterials.com",
            "phone": "+1-555-0203",
            "address": "300 Material Ave",
            "city": "Hayward",
            "state": "CA", 
            "zip": "94544",
            "terms": 45,
            "credit_limit": 50000.00
        }
    ]
    
    suppliers = {}
    for supp_data in suppliers_data:
        supplier = Supplier(
            company_id=company_id,
            supplier_code=supp_data["code"],
            name=supp_data["name"],
            contact_person=supp_data["contact"],
            email=supp_data["email"],
            phone=supp_data["phone"],
            address_line1=supp_data["address"],
            city=supp_data["city"],
            state=supp_data["state"],
            postal_code=supp_data["zip"],
            country="USA",
            payment_terms_days=supp_data["terms"],
            current_balance=Decimal('0.00'),
            is_active=True
        )
        db.add(supplier)
        suppliers[supp_data["code"]] = supplier
    
    db.commit()
    print(f"✅ Created {len(suppliers)} suppliers")
    return suppliers


def create_inventory_items(db, company_id, accounts):
    """Create inventory items with proper GL account links"""
    print("Creating Inventory Items...")
    
    # Get required GL accounts
    inventory_account = next((acc for acc in accounts.values() if acc.account_code == "1200"), None)
    cogs_account = next((acc for acc in accounts.values() if acc.account_code == "5000"), None)
    sales_account = next((acc for acc in accounts.values() if acc.account_code == "4000"), None)
    
    items_data = [
        {
            "code": "PROD001",
            "description": "Software Development Kit - Premium",
            "type": "STOCK",
            "uom": "License",
            "cost_price": 150.00,
            "selling_price": 299.99
        },
        {
            "code": "PROD002", 
            "description": "Cloud Storage Solution - 1TB",
            "type": "SERVICE",
            "uom": "Subscription",
            "cost_price": 50.00,
            "selling_price": 99.99
        },
        {
            "code": "PROD003",
            "description": "Hardware Security Module",
            "type": "STOCK",
            "uom": "Unit",
            "cost_price": 500.00,
            "selling_price": 899.99
        },
        {
            "code": "PROD004",
            "description": "Technical Support Package",
            "type": "SERVICE",
            "uom": "Hour",
            "cost_price": 75.00,
            "selling_price": 150.00
        },
        {
            "code": "PROD005",
            "description": "Enterprise Analytics Platform",
            "type": "SERVICE",
            "uom": "User",
            "cost_price": 25.00,
            "selling_price": 49.99
        }
    ]
    
    items = {}
    for item_data in items_data:
        item = InventoryItem(
            company_id=company_id,
            item_code=item_data["code"],
            description=item_data["description"],
            item_type=item_data["type"],
            unit_of_measure=item_data["uom"],
            cost_price=Decimal(str(item_data["cost_price"])),
            selling_price=Decimal(str(item_data["selling_price"])),
            quantity_on_hand=Decimal('0'),
            costing_method='WEIGHTED_AVERAGE',
            gl_asset_account_id=inventory_account.id,
            gl_expense_account_id=cogs_account.id,
            gl_revenue_account_id=sales_account.id,
            is_active=True
        )
        db.add(item)
        items[item_data["code"]] = item
    
    db.commit()
    print(f"✅ Created {len(items)} inventory items")
    return items


def create_transaction_types(db, company_id, accounts):
    """Create AR, AP, and Inventory transaction types"""
    print("Creating Transaction Types...")
    
    # Get required GL accounts
    ar_account = next((acc for acc in accounts.values() if acc.account_code == "1100"), None)
    ap_account = next((acc for acc in accounts.values() if acc.account_code == "2000"), None)
    sales_account = next((acc for acc in accounts.values() if acc.account_code == "4000"), None)
    cogs_account = next((acc for acc in accounts.values() if acc.account_code == "5000"), None)
    
    # AR Transaction Types
    ar_types_data = [
        {"code": "INV", "name": "Customer Invoice", "balance": "DEBIT"},
        {"code": "PMT", "name": "Customer Payment", "balance": "CREDIT"},
        {"code": "CN", "name": "Credit Note", "balance": "CREDIT"},
        {"code": "DN", "name": "Debit Note", "balance": "DEBIT"}
    ]
    
    ar_types = {}
    for ar_data in ar_types_data:
        ar_type = ARTransactionType(
            company_id=company_id,
            type_code=ar_data["code"],
            type_name=ar_data["name"],
            description=f"Standard {ar_data['name']}",
            gl_account_id=ar_account.id,
            default_income_account_id=sales_account.id,
            affects_balance=ar_data["balance"],
            is_active=True
        )
        db.add(ar_type)
        ar_types[ar_data["code"]] = ar_type
    
    # AP Transaction Types
    ap_types_data = [
        {"code": "BILL", "name": "Supplier Invoice", "balance": "CREDIT"},
        {"code": "PMT", "name": "Supplier Payment", "balance": "DEBIT"},
        {"code": "CN", "name": "Credit Note", "balance": "DEBIT"},
        {"code": "DN", "name": "Debit Note", "balance": "CREDIT"}
    ]
    
    ap_types = {}
    for ap_data in ap_types_data:
        ap_type = APTransactionType(
            company_id=company_id,
            type_code=ap_data["code"],
            type_name=ap_data["name"],
            description=f"Standard {ap_data['name']}",
            gl_account_id=ap_account.id,
            default_expense_account_id=cogs_account.id,
            affects_balance=ap_data["balance"],
            is_active=True
        )
        db.add(ap_type)
        ap_types[ap_data["code"]] = ap_type
    
    # Inventory Transaction Types
    inv_types_data = [
        {"code": "REC", "name": "Receipt", "effect": "INCREASE"},
        {"code": "ISS", "name": "Issue", "effect": "DECREASE"},
        {"code": "ADJ+", "name": "Positive Adjustment", "effect": "INCREASE"},
        {"code": "ADJ-", "name": "Negative Adjustment", "effect": "DECREASE"},
        {"code": "TRF", "name": "Transfer", "effect": "DECREASE"}
    ]
    
    inv_types = {}
    for inv_data in inv_types_data:
        inv_type = InventoryTransactionType(
            company_id=company_id,
            type_code=inv_data["code"],
            type_name=inv_data["name"],
            description=f"Standard {inv_data['name']}",
            affects_quantity=inv_data["effect"],
            is_active=True
        )
        db.add(inv_type)
        inv_types[inv_data["code"]] = inv_type
    
    db.commit()
    print(f"✅ Created {len(ar_types)} AR, {len(ap_types)} AP, and {len(inv_types)} inventory transaction types")
    return ar_types, ap_types, inv_types


def create_sample_transactions(db, company_id, users, accounts, customers, suppliers, items, periods, ar_types, ap_types, inv_types):
    """Create comprehensive sample transactions - 8 AR, 4 AP, 5 Inventory"""
    print("Creating Sample Transactions...")
    
    # Get current period and user
    current_period = next((p for p in periods if not p.is_closed), periods[-1])
    user = users["Accountant"]
    
    print("📊 Creating 8 AR Transactions (5 Invoices + 3 Payments)...")
    
    # AR Transactions: 5 Invoices
    invoice_type = ar_types["INV"]
    payment_type = ar_types["PMT"]
    
    invoice_data = [
        {"customer": "CUST001", "amount": 5000.00, "ref": "INV-2024-001", "desc": "Software licensing fees", "days_ago": 30},
        {"customer": "CUST002", "amount": 2500.00, "ref": "INV-2024-002", "desc": "Technical support services", "days_ago": 25},
        {"customer": "CUST003", "amount": 15000.00, "ref": "INV-2024-003", "desc": "Enterprise platform setup", "days_ago": 20},
        {"customer": "CUST001", "amount": 3200.00, "ref": "INV-2024-004", "desc": "Cloud storage subscription", "days_ago": 15},
        {"customer": "CUST002", "amount": 8500.00, "ref": "INV-2024-005", "desc": "Custom development work", "days_ago": 10}
    ]
    
    for inv_data in invoice_data:
        trans_date = datetime.now() - timedelta(days=inv_data["days_ago"])
        
        invoice = ARTransaction(
            company_id=company_id,
            customer_id=customers[inv_data["customer"]].id,
            transaction_type_id=invoice_type.id,
            transaction_date=trans_date,
            due_date=trans_date + timedelta(days=30),
            reference_number=inv_data["ref"],
            description=inv_data["desc"],
            gross_amount=Decimal(str(inv_data["amount"])),
            tax_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            net_amount=Decimal(str(inv_data["amount"])),
            outstanding_amount=Decimal(str(inv_data["amount"])),
            accounting_period_id=current_period.id,
            is_posted=True,
            posted_by=user.id,
            posted_at=datetime.now()
        )
        db.add(invoice)
        
        # Update customer balance
        customers[inv_data["customer"]].current_balance += Decimal(str(inv_data["amount"]))
    
    # AR Transactions: 3 Payments
    payment_data = [
        {"customer": "CUST001", "amount": 4000.00, "ref": "PMT-2024-001", "days_ago": 15},
        {"customer": "CUST002", "amount": 2500.00, "ref": "PMT-2024-002", "days_ago": 10},
        {"customer": "CUST003", "amount": 10000.00, "ref": "PMT-2024-003", "days_ago": 5}
    ]
    
    for pmt_data in payment_data:
        trans_date = datetime.now() - timedelta(days=pmt_data["days_ago"])
        
        payment = ARTransaction(
            company_id=company_id,
            customer_id=customers[pmt_data["customer"]].id,
            transaction_type_id=payment_type.id,
            transaction_date=trans_date,
            due_date=trans_date,
            reference_number=pmt_data["ref"],
            description=f"Payment received from {customers[pmt_data['customer']].name}",
            gross_amount=Decimal(str(pmt_data["amount"])),
            tax_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            net_amount=Decimal(str(pmt_data["amount"])),
            outstanding_amount=Decimal('0.00'),
            accounting_period_id=current_period.id,
            is_posted=True,
            posted_by=user.id,
            posted_at=datetime.now()
        )
        db.add(payment)
        
        # Update customer balance
        customers[pmt_data["customer"]].current_balance -= Decimal(str(pmt_data["amount"]))
    
    print("📋 Creating 4 AP Transactions (Bills)...")
    
    # AP Transactions: 4 Bills
    bill_type = ap_types["BILL"]
    
    bill_data = [
        {"supplier": "SUPP001", "amount": 3000.00, "ref": "BILL-2024-001", "desc": "Computer hardware purchase", "days_ago": 25},
        {"supplier": "SUPP002", "amount": 500.00, "ref": "BILL-2024-002", "desc": "Office supplies", "days_ago": 20},
        {"supplier": "SUPP003", "amount": 7500.00, "ref": "BILL-2024-003", "desc": "Raw materials", "days_ago": 15},
        {"supplier": "SUPP001", "amount": 1200.00, "ref": "BILL-2024-004", "desc": "Software licenses", "days_ago": 10}
    ]
    
    for bill_data_item in bill_data:
        trans_date = datetime.now() - timedelta(days=bill_data_item["days_ago"])
        
        bill = APTransaction(
            company_id=company_id,
            supplier_id=suppliers[bill_data_item["supplier"]].id,
            transaction_type_id=bill_type.id,
            transaction_date=trans_date,
            due_date=trans_date + timedelta(days=30),
            reference_number=bill_data_item["ref"],
            description=bill_data_item["desc"],
            gross_amount=Decimal(str(bill_data_item["amount"])),
            tax_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            net_amount=Decimal(str(bill_data_item["amount"])),
            outstanding_amount=Decimal(str(bill_data_item["amount"])),
            accounting_period_id=current_period.id,
            is_posted=True,
            posted_by=user.id,
            posted_at=datetime.now()
        )
        db.add(bill)
        
        # Update supplier balance
        suppliers[bill_data_item["supplier"]].current_balance += Decimal(str(bill_data_item["amount"]))
    
    print("📦 Creating 5 Inventory Transactions (3 Receipts + 2 Issues)...")
    
    # Inventory Transactions: 3 Receipts
    receipt_type = inv_types["REC"]
    issue_type = inv_types["ISS"]
    
    receipt_data = [
        {"item": "PROD001", "qty": 100, "cost": 150.00, "ref": "REC-2024-001", "days_ago": 20},
        {"item": "PROD003", "qty": 50, "cost": 500.00, "ref": "REC-2024-002", "days_ago": 15},
        {"item": "PROD001", "qty": 25, "cost": 145.00, "ref": "REC-2024-003", "days_ago": 10}
    ]
    
    for rec_data in receipt_data:
        trans_date = datetime.now() - timedelta(days=rec_data["days_ago"])
        
        receipt = InventoryTransaction(
            company_id=company_id,
            item_id=items[rec_data["item"]].id,
            transaction_type_id=receipt_type.id,
            transaction_date=trans_date,
            reference_number=rec_data["ref"],
            description=f"Stock receipt - {items[rec_data['item']].description}",
            quantity=Decimal(str(rec_data["qty"])),
            unit_cost=Decimal(str(rec_data["cost"])),
            total_cost=Decimal(str(rec_data["qty"])) * Decimal(str(rec_data["cost"])),
            accounting_period_id=current_period.id,
            is_posted=True,
            posted_by=user.id,
            posted_at=datetime.now()
        )
        db.add(receipt)
        
        # Update item quantity
        items[rec_data["item"]].quantity_on_hand += Decimal(str(rec_data["qty"]))
    
    # Inventory Transactions: 2 Issues
    issue_data = [
        {"item": "PROD001", "qty": 30, "cost": 150.00, "ref": "ISS-2024-001", "days_ago": 8},
        {"item": "PROD003", "qty": 10, "cost": 500.00, "ref": "ISS-2024-002", "days_ago": 5}
    ]
    
    for iss_data in issue_data:
        trans_date = datetime.now() - timedelta(days=iss_data["days_ago"])
        
        issue = InventoryTransaction(
            company_id=company_id,
            item_id=items[iss_data["item"]].id,
            transaction_type_id=issue_type.id,
            transaction_date=trans_date,
            reference_number=iss_data["ref"],
            description=f"Stock issue - {items[iss_data['item']].description}",
            quantity=Decimal(str(iss_data["qty"])),
            unit_cost=Decimal(str(iss_data["cost"])),
            total_cost=Decimal(str(iss_data["qty"])) * Decimal(str(iss_data["cost"])),
            accounting_period_id=current_period.id,
            is_posted=True,
            posted_by=user.id,
            posted_at=datetime.now()
        )
        db.add(issue)
        
        # Update item quantity
        items[iss_data["item"]].quantity_on_hand -= Decimal(str(iss_data["qty"]))
    
    db.commit()
    print("✅ Created all sample transactions:")
    print("   • 8 AR transactions (5 invoices + 3 payments)")
    print("   • 4 AP transactions (bills)")
    print("   • 5 inventory transactions (3 receipts + 2 issues)")


def create_aging_periods(db, company_id):
    """Create aging periods for AR/AP reporting"""
    print("Creating Aging Periods...")
    
    aging_periods_data = [
        {"name": "Current", "from": 0, "to": 30, "order": 1},
        {"name": "31-60 Days", "from": 31, "to": 60, "order": 2},
        {"name": "61-90 Days", "from": 61, "to": 90, "order": 3},
        {"name": "Over 90 Days", "from": 91, "to": 999, "order": 4}
    ]
    
    aging_periods = []
    for period_data in aging_periods_data:
        period = AgeingPeriod(
            company_id=company_id,
            name=period_data["name"],
            days_from=period_data["from"],
            days_to=period_data["to"],
            sort_order=period_data["order"]
        )
        db.add(period)
        aging_periods.append(period)
    
    db.commit()
    print(f"✅ Created {len(aging_periods)} aging periods")
    return aging_periods


def main():
    """Main function to create comprehensive test data"""
    print_section("rwanly ERP Comprehensive Test Data Creation")
    print("🚀 Creating complete test environment with inventory capabilities")
    print("\n📋 Test Data Summary:")
    print("   • Company, Users, and Roles")
    print("   • Chart of Accounts")
    print("   • Accounting Periods")
    print("   • 3 Customers and 3 Suppliers") 
    print("   • 5 Inventory Items")
    print("   • Transaction Types")
    print("   • 8 AR Transactions (5 invoices + 3 payments)")
    print("   • 4 AP Transactions (bills)")
    print("   • 5 Inventory Transactions (3 receipts + 2 issues)")
    print("   • Aging Periods")
    
    print("\n🔑 Login Credentials:")
    print("   Administrator: admin@techflow.com / admin123")
    print("   Accountant: accountant@techflow.com / accountant123")
    print("   Sales: sales@techflow.com / sales123")
    print("   Clerk: clerk@techflow.com / clerk123")
    
    db = SessionLocal()
    
    try:
        # Check if database is already populated
        company_count = db.query(Company).count()
        if company_count > 0:
            print("\n⚠️ Database already contains data!")
            print("Please run cleanup_database.py first if you want to start fresh.")
            return
        
        # Create company
        company = create_test_company(db)
        
        # Create users and roles
        users = create_roles_and_users(db, company.id)
        
        # Create accounting periods
        periods = create_accounting_periods(db, company.id)
        
        # Create chart of accounts
        accounts = create_chart_of_accounts(db, company.id)
        
        # Create customers
        customers = create_customers(db, company.id)
        
        # Create suppliers
        suppliers = create_suppliers(db, company.id)
        
        # Create inventory items
        items = create_inventory_items(db, company.id, accounts)
        
        # Create transaction types
        ar_types, ap_types, inv_types = create_transaction_types(db, company.id, accounts)
        
        # Create aging periods
        aging_periods = create_aging_periods(db, company.id)
        
        # Create sample transactions
        create_sample_transactions(db, company.id, users, accounts, customers, suppliers, items, periods, ar_types, ap_types, inv_types)
        
        print_section("Test Data Creation Complete")
        print("✅ All data has been successfully loaded into the database.")
        print("\n🚀 You can now start the application and log in with the credentials above.")
        
    except Exception as e:
        db.rollback()
        print("\n❌ Error creating test data:")
        print(str(e))
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    main()
