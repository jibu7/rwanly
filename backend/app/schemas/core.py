from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    company_id: int


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    address: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    address: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    permissions: List[str] = []


class RoleCreate(RoleBase):
    company_id: int


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Accounting Period Schemas
class AccountingPeriodBase(BaseModel):
    period_name: str = Field(..., max_length=100)
    start_date: date
    end_date: date
    financial_year: int
    is_closed: bool = False


class AccountingPeriodCreate(AccountingPeriodBase):
    company_id: int


class AccountingPeriodCreateRequest(AccountingPeriodBase):
    """Schema for creating accounting periods without company_id (set automatically by API)"""
    pass


class AccountingPeriodUpdate(BaseModel):
    period_name: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_closed: Optional[bool] = None


class AccountingPeriodResponse(AccountingPeriodBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# General Ledger Account Schemas
class GLAccountBase(BaseModel):
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: str = Field(..., pattern="^(ASSETS|LIABILITIES|EQUITY|REVENUE|EXPENSES)$")
    account_subtype: Optional[str] = Field(None, max_length=100)
    parent_account_id: Optional[int] = None
    is_active: bool = True
    is_control_account: bool = False
    normal_balance: str = Field(..., pattern="^(DEBIT|CREDIT)$")
    description: Optional[str] = None


class GLAccountCreate(GLAccountBase):
    company_id: int


class GLAccountCreateRequest(GLAccountBase):
    """Schema for creating GL accounts without company_id (set automatically by API)"""
    pass


class GLAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=200)
    account_type: Optional[str] = Field(None, pattern="^(ASSETS|LIABILITIES|EQUITY|REVENUE|EXPENSES)$")
    account_subtype: Optional[str] = Field(None, max_length=100)
    parent_account_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_control_account: Optional[bool] = None
    normal_balance: Optional[str] = Field(None, pattern="^(DEBIT|CREDIT)$")
    description: Optional[str] = None


class GLAccountResponse(GLAccountBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# General Ledger Transaction Schemas
class GLTransactionBase(BaseModel):
    accounting_period_id: int
    gl_account_id: int
    transaction_date: date
    reference_number: Optional[str] = Field(None, max_length=50)
    description: str = Field(..., min_length=1)
    debit_amount: Optional[float] = Field(default=0.00, ge=0)
    credit_amount: Optional[float] = Field(default=0.00, ge=0)
    source_module: Optional[str] = Field(None, max_length=50)
    source_document_id: Optional[int] = None


class GLTransactionCreate(GLTransactionBase):
    company_id: int
    posted_by: int


class GLTransactionCreateRequest(GLTransactionBase):
    """Schema for creating GL transactions without company_id and posted_by (set automatically by API)"""
    pass


class GLTransactionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    debit_amount: Optional[float] = Field(None, ge=0)
    credit_amount: Optional[float] = Field(None, ge=0)
    reference_number: Optional[str] = Field(None, max_length=50)


class GLTransactionResponse(GLTransactionBase):
    id: int
    company_id: int
    posted_by: int
    posted_at: datetime
    
    class Config:
        from_attributes = True


# Chart of Accounts Response
class ChartOfAccountsResponse(BaseModel):
    accounts: List[GLAccountResponse]
    
    class Config:
        from_attributes = True


# Trial Balance Response
class TrialBalanceItem(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    debit_balance: float
    credit_balance: float


class TrialBalanceResponse(BaseModel):
    period_id: int
    period_name: str
    as_of_date: date
    accounts: List[TrialBalanceItem]
    total_debits: float
    total_credits: float
    is_balanced: bool


# ================================
# ACCOUNTS RECEIVABLE SCHEMAS (REQ-AR-*)
# ================================

# Customer Schemas
class CustomerBase(BaseModel):
    customer_code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    credit_limit: Optional[float] = Field(0.00, ge=0)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    company_id: int


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    credit_limit: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    company_id: int
    current_balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# AR Transaction Type Schemas
class ARTransactionTypeBase(BaseModel):
    type_code: str = Field(..., max_length=20)
    type_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    gl_account_id: int
    default_income_account_id: Optional[int] = None
    affects_balance: str = Field(..., pattern="^(DEBIT|CREDIT)$")
    is_active: bool = True


class ARTransactionTypeCreate(ARTransactionTypeBase):
    company_id: int


class ARTransactionTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    gl_account_id: Optional[int] = None
    default_income_account_id: Optional[int] = None
    affects_balance: Optional[str] = Field(None, pattern="^(DEBIT|CREDIT)$")
    is_active: Optional[bool] = None


class ARTransactionTypeResponse(ARTransactionTypeBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# AR Transaction Schemas
class ARTransactionBase(BaseModel):
    customer_id: int
    transaction_type_id: int
    accounting_period_id: int
    transaction_date: date
    due_date: Optional[date] = None
    reference_number: str = Field(..., max_length=50)
    description: str
    gross_amount: float = Field(..., gt=0)
    tax_amount: Optional[float] = Field(0.00, ge=0)
    discount_amount: Optional[float] = Field(0.00, ge=0)
    source_module: str = Field("AR", max_length=50)
    source_document_id: Optional[int] = None


class ARTransactionCreate(ARTransactionBase):
    company_id: int


class ARTransactionUpdate(BaseModel):
    transaction_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    gross_amount: Optional[float] = Field(None, gt=0)
    tax_amount: Optional[float] = Field(None, ge=0)
    discount_amount: Optional[float] = Field(None, ge=0)


class ARTransactionResponse(ARTransactionBase):
    id: int
    company_id: int
    net_amount: float
    outstanding_amount: float
    is_posted: bool
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_at: datetime
    
    # Related data
    customer: Optional[CustomerResponse] = None
    transaction_type: Optional[ARTransactionTypeResponse] = None
    
    class Config:
        from_attributes = True


# AR Allocation Schemas
class ARAllocationBase(BaseModel):
    customer_id: int
    transaction_id: int  # Payment/Credit Note
    allocated_to_id: int  # Invoice
    allocation_date: date
    allocated_amount: float = Field(..., gt=0)
    reference: Optional[str] = Field(None, max_length=100)


class ARAllocationCreate(ARAllocationBase):
    company_id: int


class ARAllocationResponse(ARAllocationBase):
    id: int
    company_id: int
    posted_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ageing Period Schemas
class AgeingPeriodBase(BaseModel):
    period_name: str = Field(..., max_length=50)
    days_from: int = Field(..., ge=0)
    days_to: int = Field(..., ge=0)
    sort_order: int = Field(..., ge=1)
    is_active: bool = True


class AgeingPeriodCreate(AgeingPeriodBase):
    company_id: int


class AgeingPeriodUpdate(BaseModel):
    period_name: Optional[str] = Field(None, max_length=50)
    days_from: Optional[int] = Field(None, ge=0)
    days_to: Optional[int] = Field(None, ge=0)
    sort_order: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class AgeingPeriodResponse(AgeingPeriodBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# AR Reporting Schemas
class CustomerAgeingItem(BaseModel):
    customer_id: int
    customer_code: str
    customer_name: str
    current_balance: float
    current: float = 0.00
    period_30: float = 0.00
    period_60: float = 0.00
    period_90: float = 0.00
    over_90: float = 0.00
    total_outstanding: float


class CustomerAgeingReport(BaseModel):
    as_at_date: date
    customers: List[CustomerAgeingItem]
    summary: Dict[str, float]  # Totals by aging period


class CustomerTransactionItem(BaseModel):
    transaction_id: int
    transaction_date: date
    reference_number: str
    transaction_type: str
    description: str
    gross_amount: float
    outstanding_amount: float
    days_outstanding: Optional[int] = None


class CustomerTransactionReport(BaseModel):
    customer: CustomerResponse
    transactions: List[CustomerTransactionItem]
    summary: Dict[str, float]


# ================================
# ACCOUNTS PAYABLE SCHEMAS (REQ-AP-*)
# ================================

# Supplier Schemas
class SupplierBase(BaseModel):
    supplier_code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    credit_limit: Optional[float] = Field(0.00, ge=0)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    company_id: int


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    credit_limit: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    company_id: int
    current_balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# AP Transaction Type Schemas
class APTransactionTypeBase(BaseModel):
    type_code: str = Field(..., max_length=20)
    type_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    gl_account_id: int
    default_expense_account_id: Optional[int] = None
    affects_balance: str = Field(..., pattern="^(DEBIT|CREDIT)$")
    is_active: bool = True


class APTransactionTypeCreate(APTransactionTypeBase):
    company_id: int


class APTransactionTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    gl_account_id: Optional[int] = None
    default_expense_account_id: Optional[int] = None
    affects_balance: Optional[str] = Field(None, pattern="^(DEBIT|CREDIT)$")
    is_active: Optional[bool] = None


class APTransactionTypeResponse(APTransactionTypeBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# AP Transaction Schemas
class APTransactionBase(BaseModel):
    supplier_id: int
    transaction_type_id: int
    accounting_period_id: int
    transaction_date: date
    due_date: Optional[date] = None
    reference_number: str = Field(..., max_length=50)
    description: str
    gross_amount: float = Field(..., gt=0)
    tax_amount: Optional[float] = Field(0.00, ge=0)
    discount_amount: Optional[float] = Field(0.00, ge=0)
    source_module: str = Field("AP", max_length=50)
    source_document_id: Optional[int] = None


class APTransactionCreate(APTransactionBase):
    company_id: int


class APTransactionUpdate(BaseModel):
    transaction_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    gross_amount: Optional[float] = Field(None, gt=0)
    tax_amount: Optional[float] = Field(None, ge=0)
    discount_amount: Optional[float] = Field(None, ge=0)


class APTransactionResponse(APTransactionBase):
    id: int
    company_id: int
    net_amount: float
    outstanding_amount: float
    is_posted: bool
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_at: datetime
    
    # Related data
    supplier: Optional[SupplierResponse] = None
    transaction_type: Optional[APTransactionTypeResponse] = None
    
    class Config:
        from_attributes = True


# AP Allocation Schemas
class APAllocationBase(BaseModel):
    supplier_id: int
    transaction_id: int  # Payment/Credit Note
    allocated_to_id: int  # Invoice
    allocation_date: date
    allocated_amount: float = Field(..., gt=0)
    reference: Optional[str] = Field(None, max_length=100)


class APAllocationCreate(APAllocationBase):
    company_id: int


class APAllocationResponse(APAllocationBase):
    id: int
    company_id: int
    posted_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ================================
# INVENTORY SCHEMAS (REQ-INV-*)
# ================================

# Inventory Item Schemas
class InventoryItemBase(BaseModel):
    item_code: str = Field(..., max_length=20)
    description: str = Field(..., max_length=200)
    item_type: str = Field(..., pattern="^(STOCK|SERVICE)$")
    unit_of_measure: str = Field(..., max_length=20)
    cost_price: float = Field(0.00, ge=0)
    selling_price: float = Field(0.00, ge=0)
    costing_method: str = Field("WEIGHTED_AVERAGE", pattern="^WEIGHTED_AVERAGE$")
    gl_asset_account_id: int
    gl_expense_account_id: int
    gl_revenue_account_id: int
    is_active: bool = True


class InventoryItemCreate(InventoryItemBase):
    company_id: int


class InventoryItemUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    cost_price: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    gl_asset_account_id: Optional[int] = None
    gl_expense_account_id: Optional[int] = None
    gl_revenue_account_id: Optional[int] = None
    is_active: Optional[bool] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    company_id: int
    quantity_on_hand: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory Transaction Type Schemas
class InventoryTransactionTypeBase(BaseModel):
    type_code: str = Field(..., max_length=20)
    type_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    affects_quantity: str = Field(..., pattern="^(INCREASE|DECREASE)$")
    is_active: bool = True


class InventoryTransactionTypeCreate(InventoryTransactionTypeBase):
    company_id: int


class InventoryTransactionTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    affects_quantity: Optional[str] = Field(None, pattern="^(INCREASE|DECREASE)$")
    is_active: Optional[bool] = None


class InventoryTransactionTypeResponse(InventoryTransactionTypeBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory Transaction Schemas
class InventoryTransactionBase(BaseModel):
    item_id: int
    transaction_type_id: int
    accounting_period_id: int
    transaction_date: date
    reference_number: str = Field(..., max_length=50)
    description: str
    quantity: float = Field(..., ne=0)  # Can be positive or negative
    unit_cost: float = Field(..., gt=0)
    source_module: Optional[str] = Field("INV", max_length=50)
    source_document_id: Optional[int] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    company_id: int


class InventoryTransactionUpdate(BaseModel):
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    quantity: Optional[float] = Field(None, ne=0)
    unit_cost: Optional[float] = Field(None, gt=0)


class InventoryTransactionResponse(InventoryTransactionBase):
    id: int
    company_id: int
    total_cost: float
    is_posted: bool
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_at: datetime
    
    # Related data
    item: Optional[InventoryItemResponse] = None
    transaction_type: Optional[InventoryTransactionTypeResponse] = None
    
    class Config:
        from_attributes = True


# Inventory Reporting Schemas
class InventoryStockLevelItem(BaseModel):
    item_id: int
    item_code: str
    description: str
    unit_of_measure: str
    quantity_on_hand: float
    cost_price: float
    total_value: float


class InventoryStockLevelReport(BaseModel):
    as_at_date: date
    items: List[InventoryStockLevelItem]
    total_value: float


class InventoryTransactionHistoryItem(BaseModel):
    transaction_id: int
    transaction_date: date
    reference_number: str
    transaction_type: str
    description: str
    quantity: float
    unit_cost: float
    total_cost: float
    running_quantity: float
    running_value: float


class InventoryTransactionHistoryReport(BaseModel):
    item: InventoryItemResponse
    transactions: List[InventoryTransactionHistoryItem]
    summary: Dict[str, float]
