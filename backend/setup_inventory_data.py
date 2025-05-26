"""Setup initial inventory data for testing."""
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.core import (
    InventoryItem, InventoryTransactionType, InventoryTransaction,
    GLAccount, GLTransaction, AccountingPeriod, Company,
    Supplier, APTransactionType, APTransaction,
    Customer, ARTransactionType, ARTransaction
)


def setup_inventory_accounts(db: Session, company_id: int) -> dict:
    """Create GL accounts for inventory."""
    accounts = {
        "inventory": GLAccount(
            company_id=company_id,
            account_code="1200",
            account_name="Inventory",
            account_type="ASSETS",
            account_subtype="Current Assets",
            normal_balance="DEBIT",
            is_control_account=True,
            description="Control account for inventory items"
        ),
        "cogs": GLAccount(
            company_id=company_id,
            account_code="5000",
            account_name="Cost of Goods Sold",
            account_type="EXPENSES",
            account_subtype="Operating Expenses",
            normal_balance="DEBIT",
            description="Cost of goods sold"
        ),
        "sales": GLAccount(
            company_id=company_id,
            account_code="4000",
            account_name="Sales Revenue",
            account_type="REVENUE",
            account_subtype="Operating Revenue",
            normal_balance="CREDIT",
            description="Sales revenue from inventory items"
        ),
        "inventory_adjustment": GLAccount(
            company_id=company_id,
            account_code="5100",
            account_name="Inventory Adjustments",
            account_type="EXPENSES",
            account_subtype="Operating Expenses",
            normal_balance="DEBIT",
            description="Account for inventory adjustments and variances"
        )
    }
    
    for account in accounts.values():
        db.add(account)
    db.commit()
    
    for key in accounts:
        db.refresh(accounts[key])
    
    return accounts


def setup_transaction_types(db: Session, company_id: int) -> dict:
    """Create inventory transaction types."""
    types = {
        "purchase": InventoryTransactionType(
            company_id=company_id,
            type_code="PURCH",
            type_name="Purchase",
            description="Stock receipt from supplier",
            affects_quantity="INCREASE",
            is_active=True
        ),
        "sale": InventoryTransactionType(
            company_id=company_id,
            type_code="SALE",
            type_name="Sale",
            description="Stock issue to customer",
            affects_quantity="DECREASE",
            is_active=True
        ),
        "adjustment_in": InventoryTransactionType(
            company_id=company_id,
            type_code="ADJ-IN",
            type_name="Adjustment (Increase)",
            description="Stock adjustment - Quantity increase",
            affects_quantity="INCREASE",
            is_active=True
        ),
        "adjustment_out": InventoryTransactionType(
            company_id=company_id,
            type_code="ADJ-OUT",
            type_name="Adjustment (Decrease)",
            description="Stock adjustment - Quantity decrease",
            affects_quantity="DECREASE",
            is_active=True
        )
    }
    
    for type_obj in types.values():
        db.add(type_obj)
    db.commit()
    
    for key in types:
        db.refresh(types[key])
    
    return types


def setup_ap_transaction_types(db: Session, company_id: int, gl_accounts: dict) -> dict:
    """Create AP transaction types."""
    types = {
        "invoice": APTransactionType(
            company_id=company_id,
            type_code="INV",
            type_name="Invoice",
            description="Supplier Invoice",
            affects_balance="INCREASE",
            gl_account_id=gl_accounts["inventory"].id,  # Debit Inventory
            offset_account_id=None,  # Credit AP Control (system configured)
            is_active=True
        )
    }
    
    for type_obj in types.values():
        db.add(type_obj)
    db.commit()
    
    for key in types:
        db.refresh(types[key])
    
    return types


def setup_ar_transaction_types(db: Session, company_id: int, gl_accounts: dict) -> dict:
    """Create AR transaction types."""
    types = {
        "invoice": ARTransactionType(
            company_id=company_id,
            type_code="INV",
            type_name="Invoice",
            description="Customer Invoice",
            affects_balance="INCREASE",
            gl_account_id=gl_accounts["sales"].id,  # Credit Sales
            offset_account_id=None,  # Debit AR Control (system configured)
            is_active=True
        )
    }
    
    for type_obj in types.values():
        db.add(type_obj)
    db.commit()
    
    for key in types:
        db.refresh(types[key])
    
    return types


def setup_inventory_items(
    db: Session, company_id: int, gl_accounts: dict
) -> dict:
    """Create sample inventory items."""
    items = {
        "laptop": InventoryItem(
            company_id=company_id,
            item_code="LAP-001",
            description="Business Laptop",
            item_type="STOCK",
            unit_of_measure="UNIT",
            cost_price=800.00,
            selling_price=1200.00,
            quantity_on_hand=0,
            costing_method="WEIGHTED_AVERAGE",
            gl_asset_account_id=gl_accounts["inventory"].id,
            gl_expense_account_id=gl_accounts["cogs"].id,
            gl_revenue_account_id=gl_accounts["sales"].id,
            is_active=True
        ),
        "desktop": InventoryItem(
            company_id=company_id,
            item_code="DSK-001",
            description="Desktop Computer",
            item_type="STOCK",
            unit_of_measure="UNIT",
            cost_price=600.00,
            selling_price=900.00,
            quantity_on_hand=0,
            costing_method="WEIGHTED_AVERAGE",
            gl_asset_account_id=gl_accounts["inventory"].id,
            gl_expense_account_id=gl_accounts["cogs"].id,
            gl_revenue_account_id=gl_accounts["sales"].id,
            is_active=True
        ),
        "monitor": InventoryItem(
            company_id=company_id,
            item_code="MON-001",
            description="24-inch Monitor",
            item_type="STOCK",
            unit_of_measure="UNIT",
            cost_price=150.00,
            selling_price=250.00,
            quantity_on_hand=0,
            costing_method="WEIGHTED_AVERAGE",
            gl_asset_account_id=gl_accounts["inventory"].id,
            gl_expense_account_id=gl_accounts["cogs"].id,
            gl_revenue_account_id=gl_accounts["sales"].id,
            is_active=True
        ),
        "keyboard": InventoryItem(
            company_id=company_id,
            item_code="KBD-001",
            description="Wireless Keyboard",
            item_type="STOCK",
            unit_of_measure="UNIT",
            cost_price=40.00,
            selling_price=80.00,
            quantity_on_hand=0,
            costing_method="WEIGHTED_AVERAGE",
            gl_asset_account_id=gl_accounts["inventory"].id,
            gl_expense_account_id=gl_accounts["cogs"].id,
            gl_revenue_account_id=gl_accounts["sales"].id,
            is_active=True
        ),
        "mouse": InventoryItem(
            company_id=company_id,
            item_code="MOU-001",
            description="Wireless Mouse",
            item_type="STOCK",
            unit_of_measure="UNIT",
            cost_price=20.00,
            selling_price=45.00,
            quantity_on_hand=0,
            costing_method="WEIGHTED_AVERAGE",
            gl_asset_account_id=gl_accounts["inventory"].id,
            gl_expense_account_id=gl_accounts["cogs"].id,
            gl_revenue_account_id=gl_accounts["sales"].id,
            is_active=True
        ),
        "setup": InventoryItem(
            company_id=company_id,
            item_code="SVC-001",
            description="Computer Setup Service",
            item_type="SERVICE",
            unit_of_measure="HOUR",
            cost_price=30.00,
            selling_price=75.00,
            quantity_on_hand=0,
            costing_method="WEIGHTED_AVERAGE",
            gl_asset_account_id=gl_accounts["inventory"].id,
            gl_expense_account_id=gl_accounts["cogs"].id,
            gl_revenue_account_id=gl_accounts["sales"].id,
            is_active=True
        )
    }
    
    for item in items.values():
        db.add(item)
    db.commit()
    
    for key in items:
        db.refresh(items[key])
    
    return items


def setup_suppliers(db: Session, company_id: int) -> dict:
    """Create sample suppliers."""
    suppliers = {
        "tech_wholesale": Supplier(
            company_id=company_id,
            supplier_code="SUP-001",
            name="Tech Wholesale Ltd",
            contact_person="John Smith",
            email="john@techwholesale.com",
            phone="123-456-7890",
            address_line1="123 Supplier Street",
            city="Suppliertown",
            state="ST",
            postal_code="12345",
            country="USA",
            payment_terms_days=30,
            credit_limit=50000.00,
            is_active=True
        ),
        "pc_parts": Supplier(
            company_id=company_id,
            supplier_code="SUP-002",
            name="PC Parts Direct",
            contact_person="Alice Johnson",
            email="alice@pcparts.com",
            phone="234-567-8901",
            address_line1="456 Parts Avenue",
            city="Partsville",
            state="PS",
            postal_code="23456",
            country="USA",
            payment_terms_days=30,
            credit_limit=25000.00,
            is_active=True
        )
    }
    
    for supplier in suppliers.values():
        db.add(supplier)
    db.commit()
    
    for key in suppliers:
        db.refresh(suppliers[key])
    
    return suppliers


def setup_customers(db: Session, company_id: int) -> dict:
    """Create sample customers."""
    customers = {
        "megacorp": Customer(
            company_id=company_id,
            customer_code="CUS-001",
            name="MegaCorp Inc",
            contact_person="Sarah Wilson",
            email="sarah@megacorp.com",
            phone="345-678-9012",
            address_line1="789 Corporate Park",
            city="Megacity",
            state="MC",
            postal_code="34567",
            country="USA",
            payment_terms_days=30,
            credit_limit=20000.00,
            is_active=True
        ),
        "smallbiz": Customer(
            company_id=company_id,
            customer_code="CUS-002",
            name="SmallBiz Solutions",
            contact_person="Mike Brown",
            email="mike@smallbiz.com",
            phone="456-789-0123",
            address_line1="321 Small Street",
            city="Smalltown",
            state="SM",
            postal_code="45678",
            country="USA",
            payment_terms_days=30,
            credit_limit=10000.00,
            is_active=True
        )
    }
    
    for customer in customers.values():
        db.add(customer)
    db.commit()
    
    for key in customers:
        db.refresh(customers[key])
    
    return customers


def setup_initial_transactions(
    db: Session,
    company_id: int,
    items: dict,
    types: dict,
    posted_by: int
) -> None:
    """Create initial inventory transactions."""
    # Get current accounting period
    period = db.query(AccountingPeriod).filter(
        AccountingPeriod.company_id == company_id,
        AccountingPeriod.is_closed == False
    ).first()
    
    if not period:
        raise ValueError("No open accounting period found")
    
    # Initial stock receipts
    transactions = [
        # Laptop initial stock
        InventoryTransaction(
            company_id=company_id,
            item_id=items["laptop"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=date.today(),
            reference_number="INV-INIT-001",
            description="Initial stock setup - Laptops",
            quantity=10,
            unit_cost=800.00,
            total_cost=8000.00,
            source_module="INV",
            is_posted=True,
            posted_by=posted_by
        ),
        # Desktop initial stock
        InventoryTransaction(
            company_id=company_id,
            item_id=items["desktop"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=date.today(),
            reference_number="INV-INIT-002",
            description="Initial stock setup - Desktops",
            quantity=5,
            unit_cost=600.00,
            total_cost=3000.00,
            source_module="INV",
            is_posted=True,
            posted_by=posted_by
        ),
        # Monitor initial stock
        InventoryTransaction(
            company_id=company_id,
            item_id=items["monitor"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=date.today(),
            reference_number="INV-INIT-003",
            description="Initial stock setup - Monitors",
            quantity=20,
            unit_cost=150.00,
            total_cost=3000.00,
            source_module="INV",
            is_posted=True,
            posted_by=posted_by
        )
    ]
    
    for transaction in transactions:
        db.add(transaction)
    
    db.commit()


def create_purchase_transactions(
    db: Session,
    company_id: int,
    items: dict,
    types: dict,
    suppliers: dict,
    ap_types: dict,
    period: AccountingPeriod,
    posted_by: int
) -> None:
    """Create purchase transactions with AP integration."""
    # Purchase order from Tech Wholesale
    purchase1_date = date.today() - timedelta(days=15)
    ap_invoice1 = APTransaction(
        company_id=company_id,
        supplier_id=suppliers["tech_wholesale"].id,
        transaction_type_id=ap_types["invoice"].id,
        accounting_period_id=period.id,
        transaction_date=purchase1_date,
        due_date=purchase1_date + timedelta(days=30),
        reference_number="AP-INV-001",
        description="Initial stock purchase",
        gross_amount=Decimal("12000.00"),
        tax_amount=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        net_amount=Decimal("12000.00"),
        outstanding_amount=Decimal("12000.00"),
        source_module="AP",
        is_posted=True,
        posted_by=posted_by,
        posted_at=date.today()
    )
    db.add(ap_invoice1)
    db.flush()

    # Create inventory transactions for items in PO
    inv_transactions = [
        InventoryTransaction(
            company_id=company_id,
            item_id=items["laptop"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=purchase1_date,
            reference_number=f"PO-{ap_invoice1.reference_number}",
            description="Initial stock purchase - Laptops",
            quantity=10,
            unit_cost=800.00,
            total_cost=8000.00,
            source_module="AP",
            source_document_id=ap_invoice1.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["desktop"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=purchase1_date,
            reference_number=f"PO-{ap_invoice1.reference_number}",
            description="Initial stock purchase - Desktops",
            quantity=5,
            unit_cost=800.00,
            total_cost=4000.00,
            source_module="AP",
            source_document_id=ap_invoice1.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        )
    ]
    
    # Purchase order from PC Parts Direct
    purchase2_date = date.today() - timedelta(days=10)
    ap_invoice2 = APTransaction(
        company_id=company_id,
        supplier_id=suppliers["pc_parts"].id,
        transaction_type_id=ap_types["invoice"].id,
        accounting_period_id=period.id,
        transaction_date=purchase2_date,
        due_date=purchase2_date + timedelta(days=30),
        reference_number="AP-INV-002",
        description="Peripherals purchase",
        gross_amount=Decimal("5000.00"),
        tax_amount=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        net_amount=Decimal("5000.00"),
        outstanding_amount=Decimal("5000.00"),
        source_module="AP",
        is_posted=True,
        posted_by=posted_by,
        posted_at=date.today()
    )
    db.add(ap_invoice2)
    db.flush()

    # Add peripherals to inventory transactions
    inv_transactions.extend([
        InventoryTransaction(
            company_id=company_id,
            item_id=items["monitor"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=purchase2_date,
            reference_number=f"PO-{ap_invoice2.reference_number}",
            description="Stock purchase - Monitors",
            quantity=20,
            unit_cost=150.00,
            total_cost=3000.00,
            source_module="AP",
            source_document_id=ap_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["keyboard"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=purchase2_date,
            reference_number=f"PO-{ap_invoice2.reference_number}",
            description="Stock purchase - Keyboards",
            quantity=30,
            unit_cost=40.00,
            total_cost=1200.00,
            source_module="AP",
            source_document_id=ap_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["mouse"].id,
            transaction_type_id=types["purchase"].id,
            accounting_period_id=period.id,
            transaction_date=purchase2_date,
            reference_number=f"PO-{ap_invoice2.reference_number}",
            description="Stock purchase - Mice",
            quantity=40,
            unit_cost=20.00,
            total_cost=800.00,
            source_module="AP",
            source_document_id=ap_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        )
    ])
    
    for transaction in inv_transactions:
        db.add(transaction)
    
    db.commit()


def create_sales_transactions(
    db: Session,
    company_id: int,
    items: dict,
    types: dict,
    customers: dict,
    ar_types: dict,
    period: AccountingPeriod,
    posted_by: int
) -> None:
    """Create sales transactions with AR integration."""
    # Sale to MegaCorp
    sale1_date = date.today() - timedelta(days=5)
    ar_invoice1 = ARTransaction(
        company_id=company_id,
        customer_id=customers["megacorp"].id,
        transaction_type_id=ar_types["invoice"].id,
        accounting_period_id=period.id,
        transaction_date=sale1_date,
        due_date=sale1_date + timedelta(days=30),
        reference_number="AR-INV-001",
        description="Workstation package sale",
        gross_amount=Decimal("6000.00"),
        tax_amount=Decimal("0.00"),
        discount_amount=Decimal("300.00"),
        net_amount=Decimal("5700.00"),
        outstanding_amount=Decimal("5700.00"),
        source_module="AR",
        is_posted=True,
        posted_by=posted_by,
        posted_at=date.today()
    )
    db.add(ar_invoice1)
    db.flush()

    # Create inventory transactions for items sold
    inv_transactions = [
        InventoryTransaction(
            company_id=company_id,
            item_id=items["laptop"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale1_date,
            reference_number=f"SO-{ar_invoice1.reference_number}",
            description="Sale to MegaCorp - Laptops",
            quantity=-3,
            unit_cost=800.00,
            total_cost=2400.00,
            source_module="AR",
            source_document_id=ar_invoice1.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["monitor"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale1_date,
            reference_number=f"SO-{ar_invoice1.reference_number}",
            description="Sale to MegaCorp - Monitors",
            quantity=-3,
            unit_cost=150.00,
            total_cost=450.00,
            source_module="AR",
            source_document_id=ar_invoice1.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["keyboard"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale1_date,
            reference_number=f"SO-{ar_invoice1.reference_number}",
            description="Sale to MegaCorp - Keyboards",
            quantity=-3,
            unit_cost=40.00,
            total_cost=120.00,
            source_module="AR",
            source_document_id=ar_invoice1.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["mouse"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale1_date,
            reference_number=f"SO-{ar_invoice1.reference_number}",
            description="Sale to MegaCorp - Mice",
            quantity=-3,
            unit_cost=20.00,
            total_cost=60.00,
            source_module="AR",
            source_document_id=ar_invoice1.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
    ]

    # Sale to SmallBiz
    sale2_date = date.today() - timedelta(days=2)
    ar_invoice2 = ARTransaction(
        company_id=company_id,
        customer_id=customers["smallbiz"].id,
        transaction_type_id=ar_types["invoice"].id,
        accounting_period_id=period.id,
        transaction_date=sale2_date,
        due_date=sale2_date + timedelta(days=30),
        reference_number="AR-INV-002",
        description="Office equipment sale",
        gross_amount=Decimal("3000.00"),
        tax_amount=Decimal("0.00"),
        discount_amount=Decimal("150.00"),
        net_amount=Decimal("2850.00"),
        outstanding_amount=Decimal("2850.00"),
        source_module="AR",
        is_posted=True,
        posted_by=posted_by,
        posted_at=date.today()
    )
    db.add(ar_invoice2)
    db.flush()

    # Add items to inventory transactions
    inv_transactions.extend([
        InventoryTransaction(
            company_id=company_id,
            item_id=items["desktop"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale2_date,
            reference_number=f"SO-{ar_invoice2.reference_number}",
            description="Sale to SmallBiz - Desktops",
            quantity=-2,
            unit_cost=600.00,
            total_cost=1200.00,
            source_module="AR",
            source_document_id=ar_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["monitor"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale2_date,
            reference_number=f"SO-{ar_invoice2.reference_number}",
            description="Sale to SmallBiz - Monitors",
            quantity=-2,
            unit_cost=150.00,
            total_cost=300.00,
            source_module="AR",
            source_document_id=ar_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["keyboard"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale2_date,
            reference_number=f"SO-{ar_invoice2.reference_number}",
            description="Sale to SmallBiz - Keyboards",
            quantity=-2,
            unit_cost=40.00,
            total_cost=80.00,
            source_module="AR",
            source_document_id=ar_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        InventoryTransaction(
            company_id=company_id,
            item_id=items["mouse"].id,
            transaction_type_id=types["sale"].id,
            accounting_period_id=period.id,
            transaction_date=sale2_date,
            reference_number=f"SO-{ar_invoice2.reference_number}",
            description="Sale to SmallBiz - Mice",
            quantity=-2,
            unit_cost=20.00,
            total_cost=40.00,
            source_module="AR",
            source_document_id=ar_invoice2.id,
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        )
    ])
    
    for transaction in inv_transactions:
        db.add(transaction)
    
    db.commit()


def create_inventory_adjustments(
    db: Session,
    company_id: int,
    items: dict,
    types: dict,
    period: AccountingPeriod,
    posted_by: int
) -> None:
    """Create some inventory adjustments for testing."""
    # Stock count adjustments
    adjustment_date = date.today() - timedelta(days=1)
    adjustments = [
        # Found extra keyboard in stock count
        InventoryTransaction(
            company_id=company_id,
            item_id=items["keyboard"].id,
            transaction_type_id=types["adjustment_in"].id,
            accounting_period_id=period.id,
            transaction_date=adjustment_date,
            reference_number="ADJ-001",
            description="Stock count adjustment - Found extra keyboard",
            quantity=1,
            unit_cost=40.00,
            total_cost=40.00,
            source_module="INV",
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        ),
        # Missing mouse from stock
        InventoryTransaction(
            company_id=company_id,
            item_id=items["mouse"].id,
            transaction_type_id=types["adjustment_out"].id,
            accounting_period_id=period.id,
            transaction_date=adjustment_date,
            reference_number="ADJ-002",
            description="Stock count adjustment - Missing mouse",
            quantity=-1,
            unit_cost=20.00,
            total_cost=20.00,
            source_module="INV",
            is_posted=True,
            posted_by=posted_by,
            posted_at=date.today()
        )
    ]
    
    for adjustment in adjustments:
        db.add(adjustment)
    
    db.commit()


def main():
    """Main function to set up inventory data."""
    db = SessionLocal()
    try:
        # Get first company and active period
        company = db.query(Company).first()
        if not company:
            raise ValueError("No company found")
        
        period = db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == company.id,
            AccountingPeriod.is_closed == False
        ).first()
        if not period:
            raise ValueError("No open accounting period found")
        
        # Setup GL accounts
        print("Setting up GL accounts...")
        gl_accounts = setup_inventory_accounts(db, company.id)
        
        # Setup transaction types
        print("Setting up transaction types...")
        inv_types = setup_transaction_types(db, company.id)
        ap_types = setup_ap_transaction_types(db, company.id, gl_accounts)
        ar_types = setup_ar_transaction_types(db, company.id, gl_accounts)
        
        # Setup master data
        print("Setting up master data...")
        items = setup_inventory_items(db, company.id, gl_accounts)
        suppliers = setup_suppliers(db, company.id)
        customers = setup_customers(db, company.id)
        
        # Create purchase transactions
        print("Creating purchase transactions...")
        create_purchase_transactions(
            db, company.id, items, inv_types, suppliers, ap_types, period, posted_by=1
        )
        
        # Create sales transactions
        print("Creating sales transactions...")
        create_sales_transactions(
            db, company.id, items, inv_types, customers, ar_types, period, posted_by=1
        )
        
        # Create some inventory adjustments
        print("Creating inventory adjustments...")
        create_inventory_adjustments(
            db, company.id, items, inv_types, period, posted_by=1
        )
        
        print("Inventory setup completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
