"""
Order Entry (OE) schemas for request/response models - REQ-OE-*
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# DOCUMENT TYPE SCHEMAS
# ============================================================================

class OEDocumentTypeBase(BaseModel):
    type_code: str = Field(..., max_length=20, description="Document type code (SO, PO, GRV, INV, CN)")
    type_name: str = Field(..., max_length=100, description="Document type name")
    description: Optional[str] = None
    category: str = Field(..., max_length=20, description="SALES or PURCHASE")
    default_ar_transaction_type_id: Optional[int] = None
    default_ap_transaction_type_id: Optional[int] = None
    default_inv_transaction_type_id: Optional[int] = None
    numbering_prefix: Optional[str] = Field(None, max_length=10)
    next_number: int = Field(default=1, ge=1)
    is_active: bool = True


class OEDocumentTypeCreate(OEDocumentTypeBase):
    pass


class OEDocumentTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    default_ar_transaction_type_id: Optional[int] = None
    default_ap_transaction_type_id: Optional[int] = None
    default_inv_transaction_type_id: Optional[int] = None
    numbering_prefix: Optional[str] = Field(None, max_length=10)
    next_number: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class OEDocumentType(OEDocumentTypeBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Response type aliases for API compatibility
OEDocumentTypeResponse = OEDocumentType


# ============================================================================
# SALES ORDER SCHEMAS
# ============================================================================

class SalesOrderLineBase(BaseModel):
    line_number: int = Field(..., ge=1)
    inventory_item_id: int
    description: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal('0.00'), ge=0)


class SalesOrderLineCreate(SalesOrderLineBase):
    pass


class SalesOrderLineUpdate(BaseModel):
    line_number: Optional[int] = Field(None, ge=1)
    inventory_item_id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)


class SalesOrderLine(SalesOrderLineBase):
    id: int
    sales_order_id: int
    line_total: Decimal
    quantity_invoiced: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    document_type_id: int
    customer_id: int
    accounting_period_id: int
    order_date: date
    delivery_date: Optional[date] = None
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    line_items: List[SalesOrderLineCreate] = Field(..., min_items=1)


class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    delivery_date: Optional[date] = None
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r'^(DRAFT|CONFIRMED|INVOICED|CANCELLED)$')
    line_items: Optional[List[SalesOrderLineUpdate]] = None


class SalesOrder(SalesOrderBase):
    id: int
    company_id: int
    order_number: str
    status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    is_posted: bool
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    line_items: List[SalesOrderLine] = []

    class Config:
        from_attributes = True


# Response type aliases for API compatibility
SalesOrderResponse = SalesOrder
SalesOrderLineResponse = SalesOrderLine


# ============================================================================
# PURCHASE ORDER SCHEMAS
# ============================================================================

class PurchaseOrderLineBase(BaseModel):
    line_number: int = Field(..., ge=1)
    inventory_item_id: int
    description: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal('0.00'), ge=0)


class PurchaseOrderLineCreate(PurchaseOrderLineBase):
    pass


class PurchaseOrderLineUpdate(BaseModel):
    line_number: Optional[int] = Field(None, ge=1)
    inventory_item_id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)


class PurchaseOrderLine(PurchaseOrderLineBase):
    id: int
    purchase_order_id: int
    line_total: Decimal
    quantity_received: Decimal
    quantity_invoiced: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    document_type_id: int
    supplier_id: int
    accounting_period_id: int
    order_date: date
    delivery_date: Optional[date] = None
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    line_items: List[PurchaseOrderLineCreate] = Field(..., min_items=1)


class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    delivery_date: Optional[date] = None
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r'^(DRAFT|CONFIRMED|RECEIVED|INVOICED|CANCELLED)$')
    line_items: Optional[List[PurchaseOrderLineUpdate]] = None


class PurchaseOrder(PurchaseOrderBase):
    id: int
    company_id: int
    order_number: str
    status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    is_posted: bool
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    line_items: List[PurchaseOrderLine] = []

    class Config:
        from_attributes = True


# Response type aliases for API compatibility
PurchaseOrderResponse = PurchaseOrder
PurchaseOrderLineResponse = PurchaseOrderLine


# ============================================================================
# GOODS RECEIVED VOUCHER SCHEMAS
# ============================================================================

class GRVLineBase(BaseModel):
    line_number: int = Field(..., ge=1)
    purchase_order_line_id: int
    inventory_item_id: int
    description: Optional[str] = None
    quantity_ordered: Decimal = Field(..., gt=0)
    quantity_received: Decimal = Field(..., ge=0)
    unit_price: Decimal = Field(..., ge=0)


class GRVLineCreate(GRVLineBase):
    pass


class GRVLineUpdate(BaseModel):
    quantity_received: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None


class GRVLine(GRVLineBase):
    id: int
    grv_id: int
    line_total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class GRVBase(BaseModel):
    purchase_order_id: int
    received_date: date
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class GRVCreate(GRVBase):
    line_items: List[GRVLineCreate] = Field(..., min_items=1)


class GRVUpdate(BaseModel):
    received_date: Optional[date] = None
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r'^(RECEIVED|INVOICED)$')
    line_items: Optional[List[GRVLineUpdate]] = None


class GRV(GRVBase):
    id: int
    company_id: int
    document_type_id: int
    grv_number: str
    supplier_id: int
    accounting_period_id: int
    status: str
    total_received_value: Decimal
    is_posted: bool
    posted_by: Optional[int] = None
    posted_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    line_items: List[GRVLine] = []

    class Config:
        from_attributes = True


# Response type aliases for API compatibility
GRVResponse = GRV
GRVLineResponse = GRVLine


# ============================================================================
# CONVERT SALES ORDER TO INVOICE SCHEMA
# ============================================================================

class ConvertSalesOrderToInvoice(BaseModel):
    sales_order_id: int
    invoice_date: date
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


# ============================================================================
# REPORT SCHEMAS
# ============================================================================

class SalesOrderReport(BaseModel):
    """Sales Order listing report - REQ-OE-REPORT-001"""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    customer_id: Optional[int] = None
    status: Optional[str] = None


class PurchaseOrderReport(BaseModel):
    """Purchase Order listing report - REQ-OE-REPORT-002"""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    supplier_id: Optional[int] = None
    status: Optional[str] = None


class GRVReport(BaseModel):
    """GRV listing report - REQ-OE-REPORT-003"""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    supplier_id: Optional[int] = None
    purchase_order_id: Optional[int] = None


class GRVSummaryReportParams(BaseModel):
    """Parameters for GRV Summary Report"""
    date_from: Optional[date]
    date_to: Optional[date]
    supplier_id: Optional[int]
    status: Optional[str]
    limit: int = Field(100, ge=1, le=1000)
    skip: int = Field(0, ge=0)


# Additional schemas for API compatibility
GRVFromPOCreate = GRVCreate  # Alias for creating GRV from PO

# Report parameter schemas
SalesOrderReportParams = SalesOrderReport
PurchaseOrderReportParams = PurchaseOrderReport
GRVReportParams = GRVReport
GRVSummaryReportParams = GRVSummaryReportParams
