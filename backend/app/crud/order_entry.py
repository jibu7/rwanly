"""
Order Entry CRUD operations - REQ-OE-*
"""
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc
from datetime import date

from app.models.core import (
    OEDocumentType, SalesOrder, SalesOrderLine, PurchaseOrder, PurchaseOrderLine,
    GoodsReceivedVoucher, GRVLine, InventoryItem, Customer, Supplier
)
from app.schemas.order_entry import (
    OEDocumentTypeCreate, OEDocumentTypeUpdate,
    SalesOrderCreate, SalesOrderUpdate,
    PurchaseOrderCreate, PurchaseOrderUpdate,
    GRVCreate, GRVUpdate
)


# ============================================================================
# DOCUMENT TYPE CRUD
# ============================================================================

def get_document_types(db: Session, company_id: int, skip: int = 0, limit: int = 100) -> List[OEDocumentType]:
    """Get document types for a company - REQ-OE-DT-001"""
    return db.query(OEDocumentType).filter(
        OEDocumentType.company_id == company_id
    ).offset(skip).limit(limit).all()


def get_document_type(db: Session, company_id: int, document_type_id: int) -> Optional[OEDocumentType]:
    """Get a specific document type"""
    return db.query(OEDocumentType).filter(
        and_(
            OEDocumentType.id == document_type_id,
            OEDocumentType.company_id == company_id
        )
    ).first()


def get_document_type_by_code(db: Session, company_id: int, type_code: str) -> Optional[OEDocumentType]:
    """Get document type by code"""
    return db.query(OEDocumentType).filter(
        and_(
            OEDocumentType.company_id == company_id,
            OEDocumentType.type_code == type_code
        )
    ).first()


def create_document_type(db: Session, company_id: int, document_type: OEDocumentTypeCreate) -> OEDocumentType:
    """Create a new document type - REQ-OE-DT-001"""
    db_document_type = OEDocumentType(
        company_id=company_id,
        **document_type.dict()
    )
    db.add(db_document_type)
    db.commit()
    db.refresh(db_document_type)
    return db_document_type


def update_document_type(
    db: Session, 
    company_id: int, 
    document_type_id: int, 
    document_type_update: OEDocumentTypeUpdate
) -> Optional[OEDocumentType]:
    """Update a document type"""
    db_document_type = get_document_type(db, company_id, document_type_id)
    if db_document_type:
        update_data = document_type_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_document_type, field, value)
        db.commit()
        db.refresh(db_document_type)
    return db_document_type


# ============================================================================
# SALES ORDER CRUD
# ============================================================================

def get_sales_orders(
    db: Session, 
    company_id: int, 
    skip: int = 0, 
    limit: int = 100,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[SalesOrder]:
    """Get sales orders with optional filters - REQ-OE-SO-001"""
    query = db.query(SalesOrder).options(
        selectinload(SalesOrder.line_items),
        selectinload(SalesOrder.customer),
        selectinload(SalesOrder.document_type)
    ).filter(SalesOrder.company_id == company_id)
    
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)
    if status:
        query = query.filter(SalesOrder.status == status)
    if date_from:
        query = query.filter(SalesOrder.order_date >= date_from)
    if date_to:
        query = query.filter(SalesOrder.order_date <= date_to)
    
    return query.order_by(desc(SalesOrder.created_at)).offset(skip).limit(limit).all()


def get_sales_order(db: Session, company_id: int, sales_order_id: int) -> Optional[SalesOrder]:
    """Get a specific sales order with line items"""
    return db.query(SalesOrder).options(
        selectinload(SalesOrder.line_items),
        selectinload(SalesOrder.customer),
        selectinload(SalesOrder.document_type)
    ).filter(
        and_(
            SalesOrder.id == sales_order_id,
            SalesOrder.company_id == company_id
        )
    ).first()


def create_sales_order(db: Session, company_id: int, user_id: int, sales_order: SalesOrderCreate) -> SalesOrder:
    """Create a new sales order - REQ-OE-SO-001"""
    # Generate order number
    document_type = get_document_type(db, company_id, sales_order.document_type_id)
    if not document_type:
        raise ValueError("Invalid document type")
    
    order_number = f"{document_type.numbering_prefix or 'SO'}{document_type.next_number:06d}"
    
    # Calculate totals
    subtotal = sum(line.quantity * line.unit_price - line.discount_amount for line in sales_order.line_items)
    
    db_sales_order = SalesOrder(
        company_id=company_id,
        order_number=order_number,
        subtotal=subtotal,
        total_amount=subtotal,  # Simple calculation for MVP
        created_by=user_id,
        **sales_order.dict(exclude={'line_items'})
    )
    db.add(db_sales_order)
    db.flush()  # Get the ID
    
    # Add line items
    for line_data in sales_order.line_items:
        line_total = line_data.quantity * line_data.unit_price - line_data.discount_amount
        db_line = SalesOrderLine(
            sales_order_id=db_sales_order.id,
            line_total=line_total,
            **line_data.dict()
        )
        db.add(db_line)
    
    # Update document type next number
    document_type.next_number += 1
    
    db.commit()
    db.refresh(db_sales_order)
    return db_sales_order


def update_sales_order(
    db: Session, 
    company_id: int, 
    sales_order_id: int, 
    sales_order_update: SalesOrderUpdate
) -> Optional[SalesOrder]:
    """Update a sales order - REQ-OE-SO-002"""
    db_sales_order = get_sales_order(db, company_id, sales_order_id)
    if not db_sales_order:
        return None
    
    if db_sales_order.is_posted:
        raise ValueError("Cannot update posted sales order")
    
    update_data = sales_order_update.dict(exclude_unset=True, exclude={'line_items'})
    for field, value in update_data.items():
        setattr(db_sales_order, field, value)
    
    # Update line items if provided
    if sales_order_update.line_items is not None:
        # Remove existing lines
        db.query(SalesOrderLine).filter(SalesOrderLine.sales_order_id == sales_order_id).delete()
        
        # Add new lines
        subtotal = Decimal('0.00')
        for line_data in sales_order_update.line_items:
            line_total = line_data.quantity * line_data.unit_price - line_data.discount_amount
            subtotal += line_total
            db_line = SalesOrderLine(
                sales_order_id=sales_order_id,
                line_total=line_total,
                **line_data.dict()
            )
            db.add(db_line)
        
        db_sales_order.subtotal = subtotal
        db_sales_order.total_amount = subtotal
    
    db.commit()
    db.refresh(db_sales_order)
    return db_sales_order


def convert_sales_order_to_invoice(
    db: Session, 
    company_id: int, 
    user_id: int, 
    sales_order_id: int,
    invoice_date: date,
    reference: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """Convert Sales Order to Invoice - REQ-OE-SO-003"""
    # This would integrate with AR module when available
    # For now, return a placeholder response
    sales_order = get_sales_order(db, company_id, sales_order_id)
    if not sales_order:
        raise ValueError("Sales order not found")
    
    if sales_order.status == 'INVOICED':
        raise ValueError("Sales order already invoiced")
    
    # Update sales order status
    sales_order.status = 'INVOICED'
    db.commit()
    
    return {
        "message": "Sales order converted to invoice",
        "sales_order_id": sales_order_id,
        "invoice_reference": reference or f"INV-{sales_order.order_number}"
    }


# ============================================================================
# PURCHASE ORDER CRUD
# ============================================================================

def get_purchase_orders(
    db: Session, 
    company_id: int, 
    skip: int = 0, 
    limit: int = 100,
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[PurchaseOrder]:
    """Get purchase orders with optional filters - REQ-OE-PO-001"""
    query = db.query(PurchaseOrder).options(
        selectinload(PurchaseOrder.line_items),
        selectinload(PurchaseOrder.supplier),
        selectinload(PurchaseOrder.document_type)
    ).filter(PurchaseOrder.company_id == company_id)
    
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if date_from:
        query = query.filter(PurchaseOrder.order_date >= date_from)
    if date_to:
        query = query.filter(PurchaseOrder.order_date <= date_to)
    
    return query.order_by(desc(PurchaseOrder.created_at)).offset(skip).limit(limit).all()


def get_purchase_order(db: Session, company_id: int, purchase_order_id: int) -> Optional[PurchaseOrder]:
    """Get a specific purchase order with line items"""
    return db.query(PurchaseOrder).options(
        selectinload(PurchaseOrder.line_items),
        selectinload(PurchaseOrder.supplier),
        selectinload(PurchaseOrder.document_type)
    ).filter(
        and_(
            PurchaseOrder.id == purchase_order_id,
            PurchaseOrder.company_id == company_id
        )
    ).first()


def create_purchase_order(db: Session, company_id: int, user_id: int, purchase_order: PurchaseOrderCreate) -> PurchaseOrder:
    """Create a new purchase order - REQ-OE-PO-001"""
    # Generate order number
    document_type = get_document_type(db, company_id, purchase_order.document_type_id)
    if not document_type:
        raise ValueError("Invalid document type")
    
    order_number = f"{document_type.numbering_prefix or 'PO'}{document_type.next_number:06d}"
    
    # Calculate totals
    subtotal = sum(line.quantity * line.unit_price - line.discount_amount for line in purchase_order.line_items)
    
    db_purchase_order = PurchaseOrder(
        company_id=company_id,
        order_number=order_number,
        subtotal=subtotal,
        total_amount=subtotal,  # Simple calculation for MVP
        created_by=user_id,
        **purchase_order.dict(exclude={'line_items'})
    )
    db.add(db_purchase_order)
    db.flush()  # Get the ID
    
    # Add line items
    for line_data in purchase_order.line_items:
        line_total = line_data.quantity * line_data.unit_price - line_data.discount_amount
        db_line = PurchaseOrderLine(
            purchase_order_id=db_purchase_order.id,
            line_total=line_total,
            **line_data.dict()
        )
        db.add(db_line)
    
    # Update document type next number
    document_type.next_number += 1
    
    db.commit()
    db.refresh(db_purchase_order)
    return db_purchase_order


def update_purchase_order(
    db: Session, 
    company_id: int, 
    purchase_order_id: int, 
    purchase_order_update: PurchaseOrderUpdate
) -> Optional[PurchaseOrder]:
    """Update a purchase order - REQ-OE-PO-002"""
    db_purchase_order = get_purchase_order(db, company_id, purchase_order_id)
    if not db_purchase_order:
        return None
    
    if db_purchase_order.is_posted:
        raise ValueError("Cannot update posted purchase order")
    
    update_data = purchase_order_update.dict(exclude_unset=True, exclude={'line_items'})
    for field, value in update_data.items():
        setattr(db_purchase_order, field, value)
    
    # Update line items if provided
    if purchase_order_update.line_items is not None:
        # Remove existing lines
        db.query(PurchaseOrderLine).filter(PurchaseOrderLine.purchase_order_id == purchase_order_id).delete()
        
        # Add new lines
        subtotal = Decimal('0.00')
        for line_data in purchase_order_update.line_items:
            line_total = line_data.quantity * line_data.unit_price - line_data.discount_amount
            subtotal += line_total
            db_line = PurchaseOrderLine(
                purchase_order_id=purchase_order_id,
                line_total=line_total,
                **line_data.dict()
            )
            db.add(db_line)
        
        db_purchase_order.subtotal = subtotal
        db_purchase_order.total_amount = subtotal
    
    db.commit()
    db.refresh(db_purchase_order)
    return db_purchase_order


# ============================================================================
# GOODS RECEIVED VOUCHER CRUD
# ============================================================================

def get_grvs(
    db: Session, 
    company_id: int, 
    skip: int = 0, 
    limit: int = 100,
    supplier_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> List[GoodsReceivedVoucher]:
    """Get GRVs with optional filters"""
    query = db.query(GoodsReceivedVoucher).options(
        selectinload(GoodsReceivedVoucher.line_items),
        selectinload(GoodsReceivedVoucher.supplier),
        selectinload(GoodsReceivedVoucher.purchase_order)
    ).filter(GoodsReceivedVoucher.company_id == company_id)
    
    if supplier_id:
        query = query.filter(GoodsReceivedVoucher.supplier_id == supplier_id)
    if purchase_order_id:
        query = query.filter(GoodsReceivedVoucher.purchase_order_id == purchase_order_id)
    if date_from:
        query = query.filter(GoodsReceivedVoucher.received_date >= date_from)
    if date_to:
        query = query.filter(GoodsReceivedVoucher.received_date <= date_to)
    
    return query.order_by(desc(GoodsReceivedVoucher.created_at)).offset(skip).limit(limit).all()


def get_grv(db: Session, company_id: int, grv_id: int) -> Optional[GoodsReceivedVoucher]:
    """Get a specific GRV with line items"""
    return db.query(GoodsReceivedVoucher).options(
        selectinload(GoodsReceivedVoucher.line_items),
        selectinload(GoodsReceivedVoucher.supplier),
        selectinload(GoodsReceivedVoucher.purchase_order)
    ).filter(
        and_(
            GoodsReceivedVoucher.id == grv_id,
            GoodsReceivedVoucher.company_id == company_id
        )
    ).first()


def create_grv(db: Session, company_id: int, user_id: int, grv: GRVCreate) -> GoodsReceivedVoucher:
    """Create a new GRV - REQ-OE-PO-003"""
    # Get purchase order
    purchase_order = get_purchase_order(db, company_id, grv.purchase_order_id)
    if not purchase_order:
        raise ValueError("Purchase order not found")
    
    # Get GRV document type
    grv_doc_type = get_document_type_by_code(db, company_id, "GRV")
    if not grv_doc_type:
        raise ValueError("GRV document type not configured")
    
    # Generate GRV number
    grv_number = f"{grv_doc_type.numbering_prefix or 'GRV'}{grv_doc_type.next_number:06d}"
    
    # Calculate total received value
    total_received_value = sum(line.quantity_received * line.unit_price for line in grv.line_items)
    
    db_grv = GoodsReceivedVoucher(
        company_id=company_id,
        document_type_id=grv_doc_type.id,
        grv_number=grv_number,
        supplier_id=purchase_order.supplier_id,
        accounting_period_id=purchase_order.accounting_period_id,
        total_received_value=total_received_value,
        created_by=user_id,
        **grv.dict(exclude={'line_items'})
    )
    db.add(db_grv)
    db.flush()  # Get the ID
    
    # Add line items and update purchase order line quantities
    for line_data in grv.line_items:
        line_total = line_data.quantity_received * line_data.unit_price
        db_line = GRVLine(
            grv_id=db_grv.id,
            line_total=line_total,
            **line_data.dict()
        )
        db.add(db_line)
        
        # Update purchase order line received quantity
        po_line = db.query(PurchaseOrderLine).filter(
            PurchaseOrderLine.id == line_data.purchase_order_line_id
        ).first()
        if po_line:
            po_line.quantity_received += line_data.quantity_received
    
    # Update document type next number
    grv_doc_type.next_number += 1
    
    # Update purchase order status if fully received
    total_ordered = sum(line.quantity for line in purchase_order.line_items)
    total_received = sum(line.quantity_received for line in purchase_order.line_items)
    if total_received >= total_ordered:
        purchase_order.status = 'RECEIVED'
    
    db.commit()
    db.refresh(db_grv)
    return db_grv


def update_grv(
    db: Session, 
    company_id: int, 
    grv_id: int, 
    grv_update: GRVUpdate
) -> Optional[GoodsReceivedVoucher]:
    """Update a GRV"""
    db_grv = get_grv(db, company_id, grv_id)
    if not db_grv:
        return None
    
    if db_grv.is_posted:
        raise ValueError("Cannot update posted GRV")
    
    update_data = grv_update.dict(exclude_unset=True, exclude={'line_items'})
    for field, value in update_data.items():
        setattr(db_grv, field, value)
    
    db.commit()
    db.refresh(db_grv)
    return db_grv
