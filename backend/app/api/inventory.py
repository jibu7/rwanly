from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database.database import get_db
from app.api.auth import get_current_active_user
from app.crud.inventory import (
    InventoryItemCRUD, InventoryTransactionTypeCRUD, InventoryTransactionCRUD
)
from app.schemas.core import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryTransactionTypeCreate, InventoryTransactionTypeUpdate, InventoryTransactionTypeResponse,
    InventoryTransactionCreate, InventoryTransactionUpdate, InventoryTransactionResponse,
    InventoryStockLevelReport, InventoryTransactionHistoryReport
)
from app.core.permissions import check_permission

router = APIRouter()


# Inventory Item Endpoints
@router.post("/items", response_model=InventoryItemResponse)
def create_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    item_in: InventoryItemCreate
) -> InventoryItemResponse:
    """Create new inventory item"""
    check_permission(current_user, "inventory_items", "create")
    
    # Check if item code already exists
    if InventoryItemCRUD.get_by_code(db, company_id, item_in.item_code):
        raise HTTPException(
            status_code=400,
            detail="Item code already registered"
        )
    
    return InventoryItemCRUD.create(db, obj_in=item_in)


@router.get("/items", response_model=List[InventoryItemResponse])
def list_inventory_items(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> List[InventoryItemResponse]:
    """List inventory items"""
    check_permission(current_user, "inventory_items", "read")
    return InventoryItemCRUD.get_multi(db, company_id=company_id, skip=skip, limit=limit)


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    item_id: int
) -> InventoryItemResponse:
    """Get single inventory item by ID"""
    check_permission(current_user, "inventory_items", "read")
    item = InventoryItemCRUD.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    item_id: int,
    item_in: InventoryItemUpdate
) -> InventoryItemResponse:
    """Update an inventory item"""
    check_permission(current_user, "inventory_items", "update")
    item = InventoryItemCRUD.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return InventoryItemCRUD.update(db, db_obj=item, obj_in=item_in)


# Inventory Transaction Type Endpoints
@router.post("/transaction-types", response_model=InventoryTransactionTypeResponse)
def create_transaction_type(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    type_in: InventoryTransactionTypeCreate
) -> InventoryTransactionTypeResponse:
    """Create new transaction type"""
    check_permission(current_user, "inventory_transaction_types", "create")
    
    # Check if type code already exists
    if InventoryTransactionTypeCRUD.get_by_code(db, company_id, type_in.type_code):
        raise HTTPException(
            status_code=400,
            detail="Transaction type code already registered"
        )
    
    return InventoryTransactionTypeCRUD.create(db, obj_in=type_in)


@router.get("/transaction-types", response_model=List[InventoryTransactionTypeResponse])
def list_transaction_types(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> List[InventoryTransactionTypeResponse]:
    """List transaction types"""
    check_permission(current_user, "inventory_transaction_types", "read")
    return InventoryTransactionTypeCRUD.get_multi(
        db, company_id=company_id, skip=skip, limit=limit
    )


@router.get("/transaction-types/{type_id}", response_model=InventoryTransactionTypeResponse)
def get_transaction_type(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    type_id: int
) -> InventoryTransactionTypeResponse:
    """Get single transaction type by ID"""
    check_permission(current_user, "inventory_transaction_types", "read")
    type_obj = InventoryTransactionTypeCRUD.get(db, id=type_id)
    if not type_obj:
        raise HTTPException(status_code=404, detail="Transaction type not found")
    return type_obj


@router.put("/transaction-types/{type_id}", response_model=InventoryTransactionTypeResponse)
def update_transaction_type(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    type_id: int,
    type_in: InventoryTransactionTypeUpdate
) -> InventoryTransactionTypeResponse:
    """Update a transaction type"""
    check_permission(current_user, "inventory_transaction_types", "update")
    type_obj = InventoryTransactionTypeCRUD.get(db, id=type_id)
    if not type_obj:
        raise HTTPException(status_code=404, detail="Transaction type not found")
    return InventoryTransactionTypeCRUD.update(db, db_obj=type_obj, obj_in=type_in)


# Inventory Transaction Endpoints
@router.post("/transactions", response_model=InventoryTransactionResponse)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    transaction_in: InventoryTransactionCreate
) -> InventoryTransactionResponse:
    """Create new inventory transaction"""
    check_permission(current_user, "inventory_transactions", "create")
    try:
        return InventoryTransactionCRUD.create(
            db, obj_in=transaction_in, posted_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=List[InventoryTransactionResponse])
def list_transactions(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    item_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[InventoryTransactionResponse]:
    """List inventory transactions"""
    check_permission(current_user, "inventory_transactions", "read")
    return InventoryTransactionCRUD.get_multi(
        db, company_id=company_id, item_id=item_id, skip=skip, limit=limit
    )


@router.get("/transactions/{transaction_id}", response_model=InventoryTransactionResponse)
def get_transaction(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    transaction_id: int
) -> InventoryTransactionResponse:
    """Get single transaction by ID"""
    check_permission(current_user, "inventory_transactions", "read")
    transaction = InventoryTransactionCRUD.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


# Inventory Reports
@router.get("/reports/stock-levels", response_model=InventoryStockLevelReport)
def get_stock_level_report(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    as_at_date: Optional[date] = Query(None)
) -> InventoryStockLevelReport:
    """Get stock level report"""
    check_permission(current_user, "inventory_reports", "read")
    items = InventoryTransactionCRUD.get_stock_level_report(
        db, company_id=company_id, as_at_date=as_at_date
    )
    total_value = sum(item["total_value"] for item in items)
    return InventoryStockLevelReport(
        as_at_date=as_at_date or date.today(),
        items=items,
        total_value=total_value
    )


@router.get("/reports/transaction-history/{item_id}", response_model=InventoryTransactionHistoryReport)
def get_transaction_history_report(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    item_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None)
) -> InventoryTransactionHistoryReport:
    """Get transaction history report for an item"""
    check_permission(current_user, "inventory_reports", "read")
    
    # Get item
    item = InventoryItemCRUD.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Get transactions
    transactions = InventoryTransactionCRUD.get_transaction_history(
        db,
        company_id=company_id,
        item_id=item_id,
        from_date=from_date,
        to_date=to_date
    )
    
    # Calculate summary
    total_in = sum(t["total_cost"] for t in transactions if t["quantity"] > 0)
    total_out = sum(t["total_cost"] for t in transactions if t["quantity"] < 0)
    
    return InventoryTransactionHistoryReport(
        item=item,
        transactions=transactions,
        summary={
            "total_in": total_in,
            "total_out": total_out,
            "net_movement": total_in - total_out
        }
    )
