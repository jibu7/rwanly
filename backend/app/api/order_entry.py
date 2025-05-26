"""
Order Entry API endpoints for rwanly Core ERP system.
Implements REQ-OE-* requirements from PRD.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.auth import get_current_active_user, require_permission
from app.models.core import User
from app.crud import order_entry as oe_crud
from app.schemas import order_entry as oe_schemas

router = APIRouter()

# Document Types endpoints
@router.get("/document-types/", response_model=List[oe_schemas.OEDocumentTypeResponse])
def get_document_types(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all document types with optional company filtering."""
    require_permission(current_user, "order_entry.view")
    return oe_crud.get_document_types(db, skip=skip, limit=limit, company_id=company_id)


@router.post("/document-types/", response_model=oe_schemas.OEDocumentTypeResponse)
def create_document_type(
    document_type: oe_schemas.OEDocumentTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new document type."""
    require_permission(current_user, "order_entry.create")
    return oe_crud.create_document_type(db, document_type)


@router.get("/document-types/{document_type_id}", response_model=oe_schemas.OEDocumentTypeResponse)
def get_document_type(
    document_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific document type by ID."""
    require_permission(current_user, "order_entry.view")
    document_type = oe_crud.get_document_type(db, document_type_id)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return document_type


@router.put("/document-types/{document_type_id}", response_model=oe_schemas.OEDocumentTypeResponse)
def update_document_type(
    document_type_id: int,
    document_type_update: oe_schemas.OEDocumentTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a document type."""
    require_permission(current_user, "order_entry.edit")
    document_type = oe_crud.update_document_type(db, document_type_id, document_type_update)
    if not document_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return document_type


@router.delete("/document-types/{document_type_id}")
def delete_document_type(
    document_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a document type."""
    require_permission(current_user, "order_entry.delete")
    success = oe_crud.delete_document_type(db, document_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document type not found")
    return {"message": "Document type deleted successfully"}


# Sales Orders endpoints
@router.get("/sales-orders/", response_model=List[oe_schemas.SalesOrderResponse])
def get_sales_orders(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sales orders with optional filtering."""
    require_permission(current_user, "order_entry.view")
    return oe_crud.get_sales_orders(
        db, skip=skip, limit=limit, company_id=company_id, 
        customer_id=customer_id, status=status
    )


@router.post("/sales-orders/", response_model=oe_schemas.SalesOrderResponse)
def create_sales_order(
    sales_order: oe_schemas.SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new sales order."""
    require_permission(current_user, "order_entry.create")
    try:
        return oe_crud.create_sales_order(db, sales_order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sales-orders/{sales_order_id}", response_model=oe_schemas.SalesOrderResponse)
def get_sales_order(
    sales_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific sales order by ID."""
    require_permission(current_user, "order_entry.view")
    sales_order = oe_crud.get_sales_order(db, sales_order_id)
    if not sales_order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return sales_order


@router.put("/sales-orders/{sales_order_id}", response_model=oe_schemas.SalesOrderResponse)
def update_sales_order(
    sales_order_id: int,
    sales_order_update: oe_schemas.SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a sales order."""
    require_permission(current_user, "order_entry.edit")
    try:
        sales_order = oe_crud.update_sales_order(db, sales_order_id, sales_order_update)
        if not sales_order:
            raise HTTPException(status_code=404, detail="Sales order not found")
        return sales_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/sales-orders/{sales_order_id}")
def delete_sales_order(
    sales_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a sales order."""
    require_permission(current_user, "order_entry.delete")
    success = oe_crud.delete_sales_order(db, sales_order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return {"message": "Sales order deleted successfully"}


@router.post("/sales-orders/{sales_order_id}/confirm", response_model=oe_schemas.SalesOrderResponse)
def confirm_sales_order(
    sales_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Confirm a sales order (change status from DRAFT to CONFIRMED)."""
    require_permission(current_user, "order_entry.edit")
    try:
        sales_order = oe_crud.confirm_sales_order(db, sales_order_id)
        if not sales_order:
            raise HTTPException(status_code=404, detail="Sales order not found")
        return sales_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sales-orders/{sales_order_id}/create-invoice")
def create_invoice_from_sales_order(
    sales_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create an AR invoice from a confirmed sales order."""
    require_permission(current_user, "order_entry.edit")
    require_permission(current_user, "accounts_receivable.create")
    try:
        invoice = oe_crud.create_invoice_from_sales_order(db, sales_order_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Sales order not found or cannot be invoiced")
        return {"message": "Invoice created successfully", "invoice_id": invoice.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Purchase Orders endpoints
@router.get("/purchase-orders/", response_model=List[oe_schemas.PurchaseOrderResponse])
def get_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchase orders with optional filtering."""
    require_permission(current_user, "order_entry.view")
    return oe_crud.get_purchase_orders(
        db, skip=skip, limit=limit, company_id=company_id,
        supplier_id=supplier_id, status=status
    )


@router.post("/purchase-orders/", response_model=oe_schemas.PurchaseOrderResponse)
def create_purchase_order(
    purchase_order: oe_schemas.PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new purchase order."""
    require_permission(current_user, "order_entry.create")
    try:
        return oe_crud.create_purchase_order(db, purchase_order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/purchase-orders/{purchase_order_id}", response_model=oe_schemas.PurchaseOrderResponse)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific purchase order by ID."""
    require_permission(current_user, "order_entry.view")
    purchase_order = oe_crud.get_purchase_order(db, purchase_order_id)
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return purchase_order


@router.put("/purchase-orders/{purchase_order_id}", response_model=oe_schemas.PurchaseOrderResponse)
def update_purchase_order(
    purchase_order_id: int,
    purchase_order_update: oe_schemas.PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a purchase order."""
    require_permission(current_user, "order_entry.edit")
    try:
        purchase_order = oe_crud.update_purchase_order(db, purchase_order_id, purchase_order_update)
        if not purchase_order:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        return purchase_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/purchase-orders/{purchase_order_id}")
def delete_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a purchase order."""
    require_permission(current_user, "order_entry.delete")
    success = oe_crud.delete_purchase_order(db, purchase_order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return {"message": "Purchase order deleted successfully"}


@router.post("/purchase-orders/{purchase_order_id}/confirm", response_model=oe_schemas.PurchaseOrderResponse)
def confirm_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Confirm a purchase order (change status from DRAFT to CONFIRMED)."""
    require_permission(current_user, "order_entry.edit")
    try:
        purchase_order = oe_crud.confirm_purchase_order(db, purchase_order_id)
        if not purchase_order:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        return purchase_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Goods Received Voucher endpoints
@router.get("/grvs/", response_model=List[oe_schemas.GRVResponse])
def get_grvs(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all GRVs with optional filtering."""
    require_permission(current_user, "order_entry.view")
    return oe_crud.get_grvs(
        db, skip=skip, limit=limit, company_id=company_id,
        supplier_id=supplier_id, purchase_order_id=purchase_order_id
    )


@router.post("/grvs/", response_model=oe_schemas.GRVResponse)
def create_grv(
    grv: oe_schemas.GRVCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new GRV."""
    require_permission(current_user, "order_entry.create")
    try:
        return oe_crud.create_grv(db, grv)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/grvs/{grv_id}", response_model=oe_schemas.GRVResponse)
def get_grv(
    grv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific GRV by ID."""
    require_permission(current_user, "order_entry.view")
    grv = oe_crud.get_grv(db, grv_id)
    if not grv:
        raise HTTPException(status_code=404, detail="GRV not found")
    return grv


@router.put("/grvs/{grv_id}", response_model=oe_schemas.GRVResponse)
def update_grv(
    grv_id: int,
    grv_update: oe_schemas.GRVUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a GRV."""
    require_permission(current_user, "order_entry.edit")
    try:
        grv = oe_crud.update_grv(db, grv_id, grv_update)
        if not grv:
            raise HTTPException(status_code=404, detail="GRV not found")
        return grv
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/grvs/{grv_id}")
def delete_grv(
    grv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a GRV."""
    require_permission(current_user, "order_entry.delete")
    success = oe_crud.delete_grv(db, grv_id)
    if not success:
        raise HTTPException(status_code=404, detail="GRV not found")
    return {"message": "GRV deleted successfully"}


@router.post("/grvs/from-purchase-order/{purchase_order_id}", response_model=oe_schemas.GRVResponse)
def create_grv_from_purchase_order(
    purchase_order_id: int,
    grv_data: oe_schemas.GRVFromPOCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a GRV from a confirmed purchase order."""
    require_permission(current_user, "order_entry.create")
    try:
        grv = oe_crud.create_grv_from_purchase_order(db, purchase_order_id, grv_data)
        if not grv:
            raise HTTPException(status_code=404, detail="Purchase order not found or cannot create GRV")
        return grv
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Reports endpoints
@router.get("/reports/sales-orders")
def get_sales_orders_report(
    params: oe_schemas.SalesOrderReportParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate sales orders report."""
    require_permission(current_user, "order_entry.view")
    try:
        return oe_crud.generate_sales_orders_report(db, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/reports/purchase-orders")
def get_purchase_orders_report(
    params: oe_schemas.PurchaseOrderReportParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate purchase orders report."""
    require_permission(current_user, "order_entry.view")
    try:
        return oe_crud.generate_purchase_orders_report(db, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/reports/grv-summary")
def get_grv_summary_report(
    params: oe_schemas.GRVSummaryReportParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate GRV summary report."""
    require_permission(current_user, "order_entry.view")
    try:
        return oe_crud.generate_grv_summary_report(db, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
