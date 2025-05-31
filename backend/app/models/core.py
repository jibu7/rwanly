from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Company(Base):
    """Company model - REQ-SYS-COMP-*"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(JSONB)  # Store address as JSON
    contact_info = Column(JSONB)  # Store contact details as JSON
    settings = Column(JSONB)  # Store company-specific settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Properties to flatten JSONB data for API responses
    @property
    def street_address(self):
        return self.address.get("street_address") if self.address else None
    
    @property
    def city(self):
        return self.address.get("city") if self.address else None
    
    @property
    def state(self):
        return self.address.get("state") if self.address else None
    
    @property
    def postal_code(self):
        return self.address.get("postal_code") if self.address else None
    
    @property
    def country(self):
        return self.address.get("country") if self.address else None
    
    @property
    def phone(self):
        return self.contact_info.get("phone") if self.contact_info else None
    
    @property
    def email(self):
        return self.contact_info.get("email") if self.contact_info else None
    
    @property
    def website(self):
        return self.contact_info.get("website") if self.contact_info else None
    
    @property
    def tax_id(self):
        return self.contact_info.get("tax_id") if self.contact_info else None
    
    # Relationships
    users = relationship("User", back_populates="company")
    accounting_periods = relationship("AccountingPeriod", back_populates="company")
    gl_accounts = relationship("GLAccount", back_populates="company")
    gl_transactions = relationship("GLTransaction", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    ar_transaction_types = relationship("ARTransactionType", back_populates="company")
    ageing_periods = relationship("AgeingPeriod", back_populates="company")
    inventory_items = relationship("InventoryItem", back_populates="company")
    inventory_transaction_types = relationship("InventoryTransactionType", back_populates="company")
    inventory_transactions = relationship("InventoryTransaction", back_populates="company")
    suppliers = relationship("Supplier", back_populates="company")
    ap_transaction_types = relationship("APTransactionType", back_populates="company")
    # Order Entry relationships
    oe_document_types = relationship("OEDocumentType", back_populates="company")
    sales_orders = relationship("SalesOrder", back_populates="company")
    purchase_orders = relationship("PurchaseOrder", back_populates="company")
    grvs = relationship("GoodsReceivedVoucher", back_populates="company")


class User(Base):
    """User model - REQ-SYS-UM-*"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user")


class Role(Base):
    """Role model - REQ-SYS-RBAC-*"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    permissions = Column(JSONB)  # Store permissions as JSON array
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")


class UserRole(Base):
    """User-Role many-to-many relationship"""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class AccountingPeriod(Base):
    """Accounting Period model - REQ-SYS-PERIOD-*"""
    __tablename__ = "accounting_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)
    financial_year = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="accounting_periods")
    gl_transactions = relationship("GLTransaction", back_populates="accounting_period")


class GLAccount(Base):
    """General Ledger Account model - REQ-GL-COA-*"""
    __tablename__ = "gl_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    account_code = Column(String(20), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # ASSETS, LIABILITIES, EQUITY, REVENUE, EXPENSES
    account_subtype = Column(String(100))  # Current Assets, Fixed Assets, etc.
    parent_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_control_account = Column(Boolean, default=False)
    normal_balance = Column(String(10), nullable=False)  # DEBIT or CREDIT
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    parent_account = relationship("GLAccount", remote_side=[id])
    child_accounts = relationship("GLAccount", back_populates="parent_account")
    gl_transactions = relationship("GLTransaction", back_populates="gl_account")


class GLTransaction(Base):
    """General Ledger Transaction model - REQ-GL-TRANS-*"""
    __tablename__ = "gl_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    reference_number = Column(String(50), index=True)
    description = Column(Text, nullable=False)
    debit_amount = Column(DECIMAL(15, 2), default=0.00)
    credit_amount = Column(DECIMAL(15, 2), default=0.00)
    source_module = Column(String(50))  # AR, AP, INV, OE, MANUAL
    source_document_id = Column(Integer)  # Reference to source document
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    accounting_period = relationship("AccountingPeriod", back_populates="gl_transactions")
    gl_account = relationship("GLAccount", back_populates="gl_transactions")
    posted_by_user = relationship("User")


# ================================
# ACCOUNTS RECEIVABLE MODELS (REQ-AR-*)
# ================================

class Customer(Base):
    """Customer model - REQ-AR-CUST-*"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_code = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    payment_terms_days = Column(Integer)
    credit_limit = Column(DECIMAL(15, 2), default=0.00)
    current_balance = Column(DECIMAL(15, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="customers")
    ar_transactions = relationship("ARTransaction", back_populates="customer")
    sales_orders = relationship("SalesOrder", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(code='{self.customer_code}', name='{self.name}')>"


class ARTransactionType(Base):
    """AR Transaction Type model - REQ-AR-TT-*"""
    __tablename__ = "ar_transaction_types"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type_code = Column(String(20), nullable=False)
    type_name = Column(String(100), nullable=False)
    description = Column(Text)
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=False)  # AR Control Account
    default_income_account_id = Column(Integer, ForeignKey("gl_accounts.id"))  # Sales/Income Account
    affects_balance = Column(String(10), nullable=False)  # DEBIT or CREDIT
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="ar_transaction_types")
    gl_account = relationship("GLAccount", foreign_keys=[gl_account_id])
    default_income_account = relationship("GLAccount", foreign_keys=[default_income_account_id])
    ar_transactions = relationship("ARTransaction", back_populates="transaction_type")


class ARTransaction(Base):
    """AR Transaction model - REQ-AR-TP-*"""
    __tablename__ = "ar_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("ar_transaction_types.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    due_date = Column(Date)  # For invoices
    reference_number = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    gross_amount = Column(DECIMAL(15, 2), nullable=False)
    tax_amount = Column(DECIMAL(15, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    net_amount = Column(DECIMAL(15, 2), nullable=False)
    outstanding_amount = Column(DECIMAL(15, 2), nullable=False)  # Amount not yet allocated
    source_module = Column(String(50), default="AR")  # AR, OE
    source_document_id = Column(Integer)  # Reference to Sales Order, etc.
    is_posted = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    customer = relationship("Customer", back_populates="ar_transactions")
    transaction_type = relationship("ARTransactionType", back_populates="ar_transactions")
    accounting_period = relationship("AccountingPeriod")
    posted_by_user = relationship("User")
    allocation_lines = relationship("ARAllocation", foreign_keys="ARAllocation.transaction_id", back_populates="transaction")
    allocated_to_lines = relationship("ARAllocation", foreign_keys="ARAllocation.allocated_to_id", back_populates="allocated_to")


class ARAllocation(Base):
    """AR Allocation model - REQ-AR-ALLOC-*"""
    __tablename__ = "ar_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("ar_transactions.id"), nullable=False)  # Payment/Credit Note
    allocated_to_id = Column(Integer, ForeignKey("ar_transactions.id"), nullable=False)  # Invoice
    allocation_date = Column(Date, nullable=False)
    allocated_amount = Column(DECIMAL(15, 2), nullable=False)
    reference = Column(String(100))
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    customer = relationship("Customer")
    transaction = relationship("ARTransaction", foreign_keys=[transaction_id], back_populates="allocation_lines")
    allocated_to = relationship("ARTransaction", foreign_keys=[allocated_to_id], back_populates="allocated_to_lines")
    posted_by_user = relationship("User")


class AgeingPeriod(Base):
    """Ageing Period model - REQ-AR-AGE-*"""
    __tablename__ = "ageing_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_name = Column(String(50), nullable=False)  # "Current", "30 Days", "60 Days", etc.
    days_from = Column(Integer, nullable=False)
    days_to = Column(Integer, nullable=False)
    sort_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")


# ================================
# ACCOUNTS PAYABLE MODELS (REQ-AP-*)
# ================================

class Supplier(Base):
    """Supplier model - REQ-AP-SUPP-*"""
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    supplier_code = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    payment_terms_days = Column(Integer)
    credit_limit = Column(DECIMAL(15, 2), default=0.00)
    current_balance = Column(DECIMAL(15, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    company = relationship("Company", back_populates="suppliers")
    ap_transactions = relationship("APTransaction", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    grvs = relationship("GoodsReceivedVoucher", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(code='{self.supplier_code}', name='{self.name}')>"


class APTransactionType(Base):
    """AP Transaction Type model - REQ-AP-TT-*"""
    __tablename__ = "ap_transaction_types"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type_code = Column(String(20), nullable=False)
    type_name = Column(String(100), nullable=False)
    description = Column(Text)
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=False)  # AP Control Account
    default_expense_account_id = Column(Integer, ForeignKey("gl_accounts.id"))  # Expense Account
    affects_balance = Column(String(10), nullable=False)  # DEBIT or CREDIT
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    company = relationship("Company")
    gl_account = relationship("GLAccount", foreign_keys=[gl_account_id])
    default_expense_account = relationship("GLAccount", foreign_keys=[default_expense_account_id])
    ap_transactions = relationship("APTransaction", back_populates="transaction_type")


class APTransaction(Base):
    """AP Transaction model - REQ-AP-TP-*"""
    __tablename__ = "ap_transactions"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("ap_transaction_types.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    due_date = Column(Date)  # For invoices
    reference_number = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    gross_amount = Column(DECIMAL(15, 2), nullable=False)
    tax_amount = Column(DECIMAL(15, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    net_amount = Column(DECIMAL(15, 2), nullable=False)
    outstanding_amount = Column(DECIMAL(15, 2), nullable=False)  # Amount not yet allocated
    source_module = Column(String(50), default="AP")  # AP, OE
    source_document_id = Column(Integer)  # Reference to Purchase Order, etc.
    is_posted = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    company = relationship("Company")
    supplier = relationship("Supplier", back_populates="ap_transactions")
    transaction_type = relationship("APTransactionType", back_populates="ap_transactions")
    accounting_period = relationship("AccountingPeriod")
    posted_by_user = relationship("User")
    allocation_lines = relationship("APAllocation", foreign_keys="APAllocation.transaction_id", back_populates="transaction")
    allocated_to_lines = relationship("APAllocation", foreign_keys="APAllocation.allocated_to_id", back_populates="allocated_to")


class APAllocation(Base):
    """AP Allocation model - REQ-AP-ALLOC-*"""
    __tablename__ = "ap_allocations"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("ap_transactions.id"), nullable=False)  # Payment/Credit Note
    allocated_to_id = Column(Integer, ForeignKey("ap_transactions.id"), nullable=False)  # Invoice
    allocation_date = Column(Date, nullable=False)
    allocated_amount = Column(DECIMAL(15, 2), nullable=False)
    reference = Column(String(100))
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    company = relationship("Company")
    supplier = relationship("Supplier")
    transaction = relationship("APTransaction", foreign_keys=[transaction_id], back_populates="allocation_lines")
    allocated_to = relationship("APTransaction", foreign_keys=[allocated_to_id], back_populates="allocated_to_lines")
    posted_by_user = relationship("User")


# ================================
# INVENTORY MODELS (REQ-INV-*)
# ================================

class InventoryItem(Base):
    """Inventory Item model - REQ-INV-ITEM-*"""
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    item_code = Column(String(20), nullable=False, index=True)
    description = Column(String(200), nullable=False)
    item_type = Column(String(50), nullable=False)  # Stock, Service
    unit_of_measure = Column(String(20), nullable=False)
    cost_price = Column(DECIMAL(15, 2), nullable=True)
    selling_price = Column(DECIMAL(15, 2), nullable=True)
    quantity_on_hand = Column(DECIMAL(15, 2), default=0.00)
    costing_method = Column(String(20), default='WeightedAverage')
    reorder_level = Column(DECIMAL(15, 2), nullable=True)
    reorder_quantity = Column(DECIMAL(15, 2), nullable=True)
    gl_asset_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=True)  # Inventory Asset Account
    gl_expense_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=True)  # COGS Account
    gl_revenue_account_id = Column(Integer, ForeignKey("gl_accounts.id"), nullable=True)  # Sales Account
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    gl_asset_account = relationship("GLAccount", foreign_keys=[gl_asset_account_id])
    gl_expense_account = relationship("GLAccount", foreign_keys=[gl_expense_account_id])
    gl_revenue_account = relationship("GLAccount", foreign_keys=[gl_revenue_account_id])
    transactions = relationship("InventoryTransaction", back_populates="item")
    
    # Property mappings for frontend compatibility
    @property
    def gl_account_inventory_id(self):
        return self.gl_asset_account_id
    
    @gl_account_inventory_id.setter
    def gl_account_inventory_id(self, value):
        self.gl_asset_account_id = value
    
    @property
    def gl_account_sales_id(self):
        return self.gl_revenue_account_id
    
    @gl_account_sales_id.setter
    def gl_account_sales_id(self, value):
        self.gl_revenue_account_id = value
    
    @property
    def gl_account_cogs_id(self):
        return self.gl_expense_account_id
    
    @gl_account_cogs_id.setter
    def gl_account_cogs_id(self, value):
        self.gl_expense_account_id = value


class InventoryTransactionType(Base):
    """Inventory Transaction Type model - REQ-INV-TT-*"""
    __tablename__ = "inventory_transaction_types"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type_code = Column(String(20), nullable=False)
    type_name = Column(String(100), nullable=False)
    description = Column(Text)
    affects_quantity = Column(String(10), nullable=False)  # INCREASE or DECREASE
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    transactions = relationship("InventoryTransaction", back_populates="transaction_type")


class InventoryTransaction(Base):
    """Inventory Transaction model - REQ-INV-TRANS-*"""
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("inventory_transaction_types.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    reference_number = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    quantity = Column(DECIMAL(15, 2), nullable=False)
    unit_cost = Column(DECIMAL(15, 2), nullable=False)
    total_cost = Column(DECIMAL(15, 2), nullable=False)
    source_module = Column(String(50))  # INV, AP, AR, OE
    source_document_id = Column(Integer)  # Reference to Purchase/Sales Order, etc.
    is_posted = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    item = relationship("InventoryItem", back_populates="transactions")
    transaction_type = relationship("InventoryTransactionType", back_populates="transactions")
    accounting_period = relationship("AccountingPeriod")
    posted_by_user = relationship("User")


# ============================================================================
# ORDER ENTRY MODELS (REQ-OE-*)
# ============================================================================

class OEDocumentType(Base):
    """Order Entry Document Type model - REQ-OE-DT-*"""
    __tablename__ = "oe_document_types"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type_code = Column(String(20), nullable=False)  # SO, PO, GRV, INV, CN
    type_name = Column(String(100), nullable=False)  # Sales Order, Purchase Order, etc.
    description = Column(Text)
    category = Column(String(20), nullable=False)  # SALES, PURCHASE
    default_ar_transaction_type_id = Column(Integer, ForeignKey("ar_transaction_types.id"))  # For Sales docs
    default_ap_transaction_type_id = Column(Integer, ForeignKey("ap_transaction_types.id"))  # For Purchase docs
    default_inv_transaction_type_id = Column(Integer, ForeignKey("inventory_transaction_types.id"))
    numbering_prefix = Column(String(10))
    next_number = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    ar_transaction_type = relationship("ARTransactionType")
    ap_transaction_type = relationship("APTransactionType")
    inv_transaction_type = relationship("InventoryTransactionType")
    sales_orders = relationship("SalesOrder", back_populates="document_type")
    purchase_orders = relationship("PurchaseOrder", back_populates="document_type")
    grvs = relationship("GoodsReceivedVoucher", back_populates="document_type")


class SalesOrder(Base):
    """Sales Order model - REQ-OE-SO-*"""
    __tablename__ = "sales_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("oe_document_types.id"), nullable=False)
    order_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date)
    reference = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default='DRAFT')  # DRAFT, CONFIRMED, INVOICED, CANCELLED
    subtotal = Column(DECIMAL(15, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    tax_amount = Column(DECIMAL(15, 2), default=0.00)
    total_amount = Column(DECIMAL(15, 2), default=0.00)
    is_posted = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    document_type = relationship("OEDocumentType", back_populates="sales_orders")
    customer = relationship("Customer")
    accounting_period = relationship("AccountingPeriod")
    created_by_user = relationship("User", foreign_keys=[created_by])
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    line_items = relationship("SalesOrderLine", back_populates="sales_order", cascade="all, delete-orphan")


class SalesOrderLine(Base):
    """Sales Order Line Item model - REQ-OE-SO-*"""
    __tablename__ = "sales_order_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    description = Column(Text)
    quantity = Column(DECIMAL(15, 2), nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    discount_percent = Column(DECIMAL(5, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    line_total = Column(DECIMAL(15, 2), nullable=False)
    quantity_invoiced = Column(DECIMAL(15, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sales_order = relationship("SalesOrder", back_populates="line_items")
    inventory_item = relationship("InventoryItem")


class PurchaseOrder(Base):
    """Purchase Order model - REQ-OE-PO-*"""
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("oe_document_types.id"), nullable=False)
    order_number = Column(String(50), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date)
    reference = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default='DRAFT')  # DRAFT, CONFIRMED, RECEIVED, INVOICED, CANCELLED
    subtotal = Column(DECIMAL(15, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    tax_amount = Column(DECIMAL(15, 2), default=0.00)
    total_amount = Column(DECIMAL(15, 2), default=0.00)
    is_posted = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    document_type = relationship("OEDocumentType", back_populates="purchase_orders")
    supplier = relationship("Supplier")
    accounting_period = relationship("AccountingPeriod")
    created_by_user = relationship("User", foreign_keys=[created_by])
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    line_items = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")
    grvs = relationship("GoodsReceivedVoucher", back_populates="purchase_order")


class PurchaseOrderLine(Base):
    """Purchase Order Line Item model - REQ-OE-PO-*"""
    __tablename__ = "purchase_order_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    description = Column(Text)
    quantity = Column(DECIMAL(15, 2), nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    discount_percent = Column(DECIMAL(5, 2), default=0.00)
    discount_amount = Column(DECIMAL(15, 2), default=0.00)
    line_total = Column(DECIMAL(15, 2), nullable=False)
    quantity_received = Column(DECIMAL(15, 2), default=0.00)
    quantity_invoiced = Column(DECIMAL(15, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    inventory_item = relationship("InventoryItem")
    grv_lines = relationship("GRVLine", back_populates="purchase_order_line")


class GoodsReceivedVoucher(Base):
    """Goods Received Voucher model - REQ-OE-PO-003"""
    __tablename__ = "goods_received_vouchers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("oe_document_types.id"), nullable=False)
    grv_number = Column(String(50), nullable=False, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    accounting_period_id = Column(Integer, ForeignKey("accounting_periods.id"), nullable=False)
    received_date = Column(Date, nullable=False)
    reference = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default='RECEIVED')  # RECEIVED, INVOICED
    total_received_value = Column(DECIMAL(15, 2), default=0.00)
    is_posted = Column(Boolean, default=False)
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    document_type = relationship("OEDocumentType", back_populates="grvs")
    purchase_order = relationship("PurchaseOrder", back_populates="grvs")
    supplier = relationship("Supplier")
    accounting_period = relationship("AccountingPeriod")
    created_by_user = relationship("User", foreign_keys=[created_by])
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    line_items = relationship("GRVLine", back_populates="grv", cascade="all, delete-orphan")


class GRVLine(Base):
    """GRV Line Item model"""
    __tablename__ = "grv_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    grv_id = Column(Integer, ForeignKey("goods_received_vouchers.id"), nullable=False)
    purchase_order_line_id = Column(Integer, ForeignKey("purchase_order_lines.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    description = Column(Text)
    quantity_ordered = Column(DECIMAL(15, 2), nullable=False)
    quantity_received = Column(DECIMAL(15, 2), nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    line_total = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    grv = relationship("GoodsReceivedVoucher", back_populates="line_items")
    purchase_order_line = relationship("PurchaseOrderLine", back_populates="grv_lines")
    inventory_item = relationship("InventoryItem")
