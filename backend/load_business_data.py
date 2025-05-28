#!/usr/bin/env python3
"""
Comprehensive Business Data Setup Script
This script loads typical business data for a functional ERP system including:
- Chart of Accounts
- Customers and Suppliers
- Inventory Items
- Sample Transactions
- Accounting Periods
"""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.core import *
from app.core.security import get_password_hash


class BusinessDataLoader:
    """Loads comprehensive business data for ERP system."""
    
    def __init__(self, db: Session):
        self.db = db
        self.company = None
        self.admin_user = None
        self.accounts = {}
        self.customers = {}
        self.suppliers = {}
        self.inventory_items = {}
        self.transaction_types = {}
        self.document_types = {}
        self.accounting_period = None
    
    def load_all_data(self):
        """Load all business data in proper sequence."""
        try:
            print("🏢 Setting up comprehensive business data...")
            
            self.create_company()
            self.create_admin_user()
            self.create_accounting_periods()
            self.create_chart_of_accounts()
            self.create_transaction_types()
            self.create_document_types()
            self.create_customers()
            self.create_suppliers()
            self.create_inventory_items()
            self.create_sample_transactions()
            
            self.db.commit()
            print("\n✅ All business data loaded successfully!")
            
        except Exception as e:
            self.db.rollback()
            print(f"\n❌ Error loading data: {str(e)}")
            raise
    
    def create_company(self):
        """Create the main company."""
        print("\n📋 Creating company...")
        
        self.company = Company(
            name="TechFlow Solutions Inc.",
            address={
                "street": "123 Business Plaza",
                "city": "Tech City",
                "state": "CA",
                "postal_code": "90210",
                "country": "USA"
            },
            contact_info={
                "phone": "+1-555-0123",
                "email": "info@techflow.com",
                "website": "www.techflow.com"
            },
            settings={
                "currency": "USD",
                "fiscal_year_end": "12-31",
                "default_tax_rate": 8.5
            }
        )
        
        self.db.add(self.company)
        self.db.flush()
        print(f"  ✓ Company created: {self.company.name} (ID: {self.company.id})")
    
    def create_admin_user(self):
        """Create admin user and other role-based users."""
        print("\n👤 Creating users with roles...")
        
        # Create roles with permissions
        roles_data = [
            ("Administrator", "Full system access", ["all"]),
            ("Accountant", "Accounting and financial access", ["gl", "ar", "ap", "reports"]),
            ("Sales", "Sales and customer management", ["ar", "customers", "sales_orders"]),
            ("Clerk", "Basic data entry access", ["data_entry", "basic_reports"]),
        ]
        
        roles = {}
        for role_name, description, permissions in roles_data:
            role = Role(
                name=role_name,
                description=description,
                company_id=self.company.id,
                permissions=permissions
            )
            self.db.add(role)
            roles[role_name] = role
        
        self.db.flush()
        
        # Create users with proper credentials
        users_data = [
            ("admin", "admin@techflow.com", "admin123", "System", "Administrator", "Administrator"),
            ("accountant", "accountant@techflow.com", "accountant123", "Finance", "Manager", "Accountant"),
            ("sales", "sales@techflow.com", "sales123", "Sales", "Representative", "Sales"),
            ("clerk", "clerk@techflow.com", "clerk123", "Data", "Clerk", "Clerk"),
        ]
        
        for username, email, password, first_name, last_name, role_name in users_data:
            # Hash the password properly using bcrypt
            user = User(
                username=username,
                email=email,
                password_hash=get_password_hash(password),
                company_id=self.company.id,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            self.db.add(user)
            self.db.flush()
            
            # Assign role
            user_role = UserRole(user_id=user.id, role_id=roles[role_name].id)
            self.db.add(user_role)
            
            if username == "admin":
                self.admin_user = user
            
            print(f"  ✓ User created: {username} ({email}) - Role: {role_name}")
        
        print(f"  ✓ Created {len(users_data)} users with roles")
    
    def create_accounting_periods(self):
        """Create accounting periods for current and next year."""
        print("\n📅 Creating accounting periods...")
        
        current_year = date.today().year
        
        # Current year periods
        for month in range(1, 13):
            start_date = date(current_year, month, 1)
            if month == 12:
                end_date = date(current_year, 12, 31)
            else:
                end_date = date(current_year, month + 1, 1) - timedelta(days=1)
            
            period = AccountingPeriod(
                company_id=self.company.id,
                period_name=f"{current_year}-{month:02d}",
                start_date=start_date,
                end_date=end_date,
                financial_year=current_year,
                is_closed=month < date.today().month  # Close past months
            )
            self.db.add(period)
            
            # Store current period for transactions
            if month == date.today().month:
                self.accounting_period = period
        
        self.db.flush()
        print(f"  ✓ Created 12 accounting periods for {current_year}")
    
    def create_chart_of_accounts(self):
        """Create comprehensive chart of accounts."""
        print("\n💰 Creating chart of accounts...")
        
        accounts_data = [
            # ASSETS
            ("1000", "Cash and Cash Equivalents", "ASSETS", "Current Assets", "DEBIT"),
            ("1010", "Petty Cash", "ASSETS", "Current Assets", "DEBIT"),
            ("1020", "Checking Account", "ASSETS", "Current Assets", "DEBIT"),
            ("1030", "Savings Account", "ASSETS", "Current Assets", "DEBIT"),
            ("1100", "Accounts Receivable", "ASSETS", "Current Assets", "DEBIT"),
            ("1200", "Inventory", "ASSETS", "Current Assets", "DEBIT"),
            ("1300", "Prepaid Expenses", "ASSETS", "Current Assets", "DEBIT"),
            ("1400", "Office Equipment", "ASSETS", "Fixed Assets", "DEBIT"),
            ("1450", "Accumulated Depreciation - Equipment", "ASSETS", "Fixed Assets", "CREDIT"),
            ("1500", "Computer Equipment", "ASSETS", "Fixed Assets", "DEBIT"),
            ("1550", "Accumulated Depreciation - Computers", "ASSETS", "Fixed Assets", "CREDIT"),
            
            # LIABILITIES
            ("2000", "Accounts Payable", "LIABILITIES", "Current Liabilities", "CREDIT"),
            ("2100", "Accrued Expenses", "LIABILITIES", "Current Liabilities", "CREDIT"),
            ("2200", "Sales Tax Payable", "LIABILITIES", "Current Liabilities", "CREDIT"),
            ("2300", "Short-term Loans", "LIABILITIES", "Current Liabilities", "CREDIT"),
            ("2400", "Long-term Debt", "LIABILITIES", "Long-term Liabilities", "CREDIT"),
            
            # EQUITY
            ("3000", "Owner's Equity", "EQUITY", "Owner's Equity", "CREDIT"),
            ("3100", "Retained Earnings", "EQUITY", "Owner's Equity", "CREDIT"),
            ("3200", "Current Year Earnings", "EQUITY", "Owner's Equity", "CREDIT"),
            
            # REVENUE
            ("4000", "Sales Revenue", "REVENUE", "Operating Revenue", "CREDIT"),
            ("4100", "Service Revenue", "REVENUE", "Operating Revenue", "CREDIT"),
            ("4200", "Interest Income", "REVENUE", "Other Income", "CREDIT"),
            ("4300", "Other Income", "REVENUE", "Other Income", "CREDIT"),
            
            # EXPENSES
            ("5000", "Cost of Goods Sold", "EXPENSES", "Cost of Sales", "DEBIT"),
            ("5100", "Purchase Discounts", "EXPENSES", "Cost of Sales", "CREDIT"),
            ("6000", "Salaries and Wages", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6100", "Employee Benefits", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6200", "Rent Expense", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6300", "Utilities", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6400", "Office Supplies", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6500", "Marketing and Advertising", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6600", "Professional Services", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6700", "Insurance", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6800", "Depreciation Expense", "EXPENSES", "Operating Expenses", "DEBIT"),
            ("6900", "Interest Expense", "EXPENSES", "Financial Expenses", "DEBIT"),
            ("7000", "Bank Charges", "EXPENSES", "Financial Expenses", "DEBIT"),
        ]
        
        for code, name, acc_type, subtype, balance in accounts_data:
            account = GLAccount(
                company_id=self.company.id,
                account_code=code,
                account_name=name,
                account_type=acc_type,
                account_subtype=subtype,
                normal_balance=balance,
                is_active=True,
                description=f"Standard {acc_type.lower()} account"
            )
            self.db.add(account)
            self.accounts[code] = account
        
        self.db.flush()
        print(f"  ✓ Created {len(accounts_data)} GL accounts")
    
    def create_transaction_types(self):
        """Create transaction types for AR, AP, and Inventory."""
        print("\n📝 Creating transaction types...")
        
        # AR Transaction Types
        ar_types = [
            ("INV", "Sales Invoice", "Invoice to customer", "1100", "4000", "DEBIT"),
            ("PMT", "Customer Payment", "Payment from customer", "1100", "1000", "CREDIT"),
            ("CN", "Credit Note", "Credit note to customer", "1100", "4000", "CREDIT"),
        ]
        
        for code, name, desc, ar_account, default_account, affects in ar_types:
            ar_type = ARTransactionType(
                company_id=self.company.id,
                type_code=code,
                type_name=name,
                description=desc,
                gl_account_id=self.accounts[ar_account].id,
                default_income_account_id=self.accounts[default_account].id,
                affects_balance=affects,
                is_active=True
            )
            self.db.add(ar_type)
            self.transaction_types[f"AR_{code}"] = ar_type
        
        # AP Transaction Types
        ap_types = [
            ("BILL", "Supplier Invoice", "Invoice from supplier", "2000", "5000", "CREDIT"),
            ("PMT", "Supplier Payment", "Payment to supplier", "2000", "1000", "DEBIT"),
            ("CN", "Credit Note", "Credit note from supplier", "2000", "5000", "DEBIT"),
        ]
        
        for code, name, desc, ap_account, default_account, affects in ap_types:
            ap_type = APTransactionType(
                company_id=self.company.id,
                type_code=code,
                type_name=name,
                description=desc,
                gl_account_id=self.accounts[ap_account].id,
                default_expense_account_id=self.accounts[default_account].id,
                affects_balance=affects,
                is_active=True
            )
            self.db.add(ap_type)
            self.transaction_types[f"AP_{code}"] = ap_type
        
        # Inventory Transaction Types
        inv_types = [
            ("PURCH", "Purchase Receipt", "INCREASE"),
            ("SALE", "Sales Issue", "DECREASE"),
            ("ADJ_IN", "Adjustment In", "INCREASE"),
            ("ADJ_OUT", "Adjustment Out", "DECREASE"),
        ]
        
        for code, name, affects in inv_types:
            inv_type = InventoryTransactionType(
                company_id=self.company.id,
                type_code=code,
                type_name=name,
                description=f"Inventory {name.lower()}",
                affects_quantity=affects,
                is_active=True
            )
            self.db.add(inv_type)
            self.transaction_types[f"INV_{code}"] = inv_type
        
        self.db.flush()
        print(f"  ✓ Created AR, AP, and Inventory transaction types")
    
    def create_document_types(self):
        """Create document types for Order Entry."""
        print("\n📄 Creating document types...")
        
        doc_types = [
            ("SO", "Sales Order", "SALES", None, None, "SALE"),
            ("PO", "Purchase Order", "PURCHASE", None, "BILL", "PURCH"),
            ("GRV", "Goods Received Voucher", "PURCHASE", None, None, "PURCH"),
        ]
        
        for code, name, category, ar_type, ap_type, inv_type in doc_types:
            doc_type = OEDocumentType(
                company_id=self.company.id,
                type_code=code,
                type_name=name,
                description=f"Standard {name}",
                category=category,
                default_ar_transaction_type_id=self.transaction_types.get(f"AR_{ar_type}").id if ar_type else None,
                default_ap_transaction_type_id=self.transaction_types.get(f"AP_{ap_type}").id if ap_type else None,
                default_inv_transaction_type_id=self.transaction_types[f"INV_{inv_type}"].id,
                numbering_prefix=code,
                next_number=1001,
                is_active=True
            )
            self.db.add(doc_type)
            self.document_types[code] = doc_type
        
        self.db.flush()
        print(f"  ✓ Created {len(doc_types)} document types")
    
    def create_customers(self):
        """Create sample customers."""
        print("\n👥 Creating customers...")
        
        customers_data = [
            ("CUST001", "ABC Corporation", "John Smith", "john@abc-corp.com", "+1-555-0101", 30, 10000),
            ("CUST002", "XYZ Industries", "Sarah Johnson", "sarah@xyz-ind.com", "+1-555-0102", 45, 15000),
            ("CUST003", "Global Tech Solutions", "Mike Davis", "mike@globaltech.com", "+1-555-0103", 30, 25000),
            ("CUST004", "Metro Services LLC", "Lisa Chen", "lisa@metroservices.com", "+1-555-0104", 60, 8000),
            ("CUST005", "Innovation Labs", "David Wilson", "david@innovationlabs.com", "+1-555-0105", 30, 20000),
        ]
        
        for code, name, contact, email, phone, terms, limit in customers_data:
            customer = Customer(
                company_id=self.company.id,
                customer_code=code,
                name=name,
                contact_person=contact,
                email=email,
                phone=phone,
                address_line1="123 Business Street",
                city="Business City",
                state="CA",
                postal_code="90210",
                country="USA",
                payment_terms_days=terms,
                credit_limit=Decimal(str(limit)),
                current_balance=Decimal('0.00'),
                is_active=True
            )
            self.db.add(customer)
            self.customers[code] = customer
        
        self.db.flush()
        print(f"  ✓ Created {len(customers_data)} customers")
    
    def create_suppliers(self):
        """Create sample suppliers."""
        print("\n🏭 Creating suppliers...")
        
        suppliers_data = [
            ("SUPP001", "Tech Components Inc.", "Robert Brown", "robert@techcomp.com", "+1-555-0201", 30),
            ("SUPP002", "Office Supplies Co.", "Emma White", "emma@officesupplies.com", "+1-555-0202", 45),
            ("SUPP003", "Hardware Solutions", "James Green", "james@hardwaresol.com", "+1-555-0203", 30),
            ("SUPP004", "Software Vendors Ltd.", "Anna Black", "anna@softwarevendors.com", "+1-555-0204", 60),
            ("SUPP005", "Equipment Rental Co.", "Tom Gray", "tom@equiprental.com", "+1-555-0205", 15),
        ]
        
        for code, name, contact, email, phone, terms in suppliers_data:
            supplier = Supplier(
                company_id=self.company.id,
                supplier_code=code,
                name=name,
                contact_person=contact,
                email=email,
                phone=phone,
                address_line1="456 Supplier Avenue",
                city="Supplier City",
                state="CA",
                postal_code="90211",
                country="USA",
                payment_terms_days=terms,
                current_balance=Decimal('0.00'),
                is_active=True
            )
            self.db.add(supplier)
            self.suppliers[code] = supplier
        
        self.db.flush()
        print(f"  ✓ Created {len(suppliers_data)} suppliers")
    
    def create_inventory_items(self):
        """Create sample inventory items."""
        print("\n📦 Creating inventory items...")
        
        items_data = [
            # Code, Description, Type, UOM, Cost, Selling Price, Initial Qty
            ("LAPTOP001", "Business Laptop - Dell Inspiron", "STOCK", "EA", 800.00, 1200.00, 50),
            ("LAPTOP002", "Gaming Laptop - ASUS ROG", "STOCK", "EA", 1200.00, 1800.00, 25),
            ("DESKTOP001", "Desktop Computer - HP Elite", "STOCK", "EA", 600.00, 900.00, 30),
            ("MONITOR001", "24-inch LED Monitor", "STOCK", "EA", 200.00, 300.00, 75),
            ("KEYBOARD001", "Wireless Keyboard", "STOCK", "EA", 50.00, 80.00, 100),
            ("MOUSE001", "Optical Mouse", "STOCK", "EA", 25.00, 40.00, 150),
            ("PRINTER001", "Laser Printer - HP LaserJet", "STOCK", "EA", 300.00, 450.00, 20),
            ("CABLE001", "USB-C Cable 6ft", "STOCK", "EA", 15.00, 25.00, 200),
            ("SOFTWARE001", "Office Suite License", "STOCK", "EA", 80.00, 120.00, 100),
            ("SERVICE001", "Technical Support Service", "SERVICE", "HR", 0.00, 75.00, 0),
            ("SERVICE002", "Installation Service", "SERVICE", "HR", 0.00, 100.00, 0),
            ("SERVICE003", "Training Service", "SERVICE", "HR", 0.00, 85.00, 0),
        ]
        
        for code, desc, item_type, uom, cost, selling, qty in items_data:
            item = InventoryItem(
                company_id=self.company.id,
                item_code=code,
                description=desc,
                item_type=item_type,
                unit_of_measure=uom,
                cost_price=Decimal(str(cost)),
                selling_price=Decimal(str(selling)),
                quantity_on_hand=Decimal(str(qty)),
                costing_method='WEIGHTED_AVERAGE',
                gl_asset_account_id=self.accounts["1200"].id,  # Inventory
                gl_expense_account_id=self.accounts["5000"].id,  # COGS
                gl_revenue_account_id=self.accounts["4000"].id,  # Sales
                is_active=True
            )
            self.db.add(item)
            self.inventory_items[code] = item
        
        self.db.flush()
        print(f"  ✓ Created {len(items_data)} inventory items")
    
    def create_sample_transactions(self):
        """Create sample business transactions."""
        print("\n💸 Creating sample transactions...")
        
        # Get current date and some past dates
        today = date.today()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        transaction_count = 0
        
        # Sample Customer Invoices
        sample_invoices = [
            ("CUST001", last_month, "INV-001", "Monthly services", 2500.00),
            ("CUST002", last_week, "INV-002", "Hardware delivery", 4800.00),
            ("CUST003", today, "INV-003", "Software licenses", 1800.00),
        ]
        
        for cust_code, trans_date, ref, desc, amount in sample_invoices:
            invoice = ARTransaction(
                company_id=self.company.id,
                customer_id=self.customers[cust_code].id,
                transaction_type_id=self.transaction_types["AR_INV"].id,
                transaction_date=trans_date,
                due_date=trans_date + timedelta(days=30),
                reference_number=ref,
                description=desc,
                gross_amount=Decimal(str(amount)),
                tax_amount=Decimal('0.00'),
                discount_amount=Decimal('0.00'),
                net_amount=Decimal(str(amount)),
                outstanding_amount=Decimal(str(amount)),
                accounting_period_id=self.accounting_period.id,
                is_posted=True,
                posted_by=self.admin_user.id,
                posted_at=datetime.now()
            )
            self.db.add(invoice)
            transaction_count += 1
        
        # Sample Supplier Bills
        sample_bills = [
            ("SUPP001", last_month, "BILL-001", "Component purchase", 3200.00),
            ("SUPP002", last_week, "BILL-002", "Office supplies", 850.00),
            ("SUPP004", today, "BILL-003", "Software licensing", 1500.00),
        ]
        
        for supp_code, trans_date, ref, desc, amount in sample_bills:
            bill = APTransaction(
                company_id=self.company.id,
                supplier_id=self.suppliers[supp_code].id,
                transaction_type_id=self.transaction_types["AP_BILL"].id,
                transaction_date=trans_date,
                due_date=trans_date + timedelta(days=30),
                reference_number=ref,
                description=desc,
                gross_amount=Decimal(str(amount)),
                tax_amount=Decimal('0.00'),
                discount_amount=Decimal('0.00'),
                net_amount=Decimal(str(amount)),
                outstanding_amount=Decimal(str(amount)),
                accounting_period_id=self.accounting_period.id,
                is_posted=True,
                posted_by=self.admin_user.id,
                posted_at=datetime.now()
            )
            self.db.add(bill)
            transaction_count += 1
        
        # Sample Inventory Transactions
        sample_inventory = [
            ("LAPTOP001", "PURCH", last_month, "INV-PURCH-001", "Initial stock purchase", 20, 800.00),
            ("MONITOR001", "PURCH", last_week, "INV-PURCH-002", "Monitor restock", 30, 200.00),
            ("LAPTOP001", "SALE", today, "INV-SALE-001", "Sale to customer", 5, 800.00),
        ]
        
        for item_code, trans_type, trans_date, ref, desc, qty, cost in sample_inventory:
            inventory_transaction = InventoryTransaction(
                company_id=self.company.id,
                item_id=self.inventory_items[item_code].id,
                transaction_type_id=self.transaction_types[f"INV_{trans_type}"].id,
                transaction_date=trans_date,
                reference_number=ref,
                description=desc,
                quantity=Decimal(str(qty)),
                unit_cost=Decimal(str(cost)),
                total_cost=Decimal(str(qty)) * Decimal(str(cost)),
                accounting_period_id=self.accounting_period.id,
                is_posted=True,
                posted_by=self.admin_user.id,
                posted_at=datetime.now()
            )
            self.db.add(inventory_transaction)
            transaction_count += 1
        
        self.db.flush()
        print(f"  ✓ Created {transaction_count} sample transactions")


def main():
    """Main function to load business data."""
    print("=" * 70)
    print("🚀 COMPREHENSIVE BUSINESS DATA LOADER")
    print("=" * 70)
    print("This script will load typical business data for a functional ERP system.")
    print()
    
    # Check if database is clean
    db = SessionLocal()
    try:
        company_count = db.query(Company).count()
        if company_count > 0:
            print(f"⚠️  Warning: Found {company_count} existing companies in database.")
            print("Run cleanup_database.py first to avoid duplicates.")
            choice = input("Continue anyway? (y/N): ")
            if choice.lower() != 'y':
                print("❌ Data loading cancelled.")
                return 1
        
        # Load all business data
        loader = BusinessDataLoader(db)
        loader.load_all_data()
        
        print("\n" + "=" * 70)
        print("✅ BUSINESS DATA LOADING COMPLETED!")
        print("=" * 70)
        print("Your ERP system now has:")
        print("  📊 Complete Chart of Accounts")
        print("  👥 Sample Customers and Suppliers")
        print("  📦 Inventory Items with Stock")
        print("  💸 Sample Transactions")
        print("  📅 Accounting Periods")
        print("  👤 User Accounts:")
        print("     - Administrator: admin@techflow.com / admin123")
        print("     - Accountant: accountant@techflow.com / accountant123") 
        print("     - Sales: sales@techflow.com / sales123")
        print("     - Clerk: clerk@techflow.com / clerk123")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ DATA LOADING FAILED: {str(e)}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
