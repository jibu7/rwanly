from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database.database import get_db
from app.api.auth import get_current_active_user, require_permission
from app.models.core import User, InventoryItem, InventoryTransactionType, GLAccount
from app.schemas.core import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryTransactionTypeCreate, InventoryTransactionTypeResponse,
    InventoryTransactionCreate, InventoryTransactionResponse
)
from app.crud.inventory import InventoryItemCRUD, InventoryTransactionTypeCRUD, InventoryTransactionCRUD
from app.core.permissions import Permissions

router = APIRouter()


# Inventory Item Endpoints
@router.get("/items", response_model=List[InventoryItemResponse])
def list_inventory_items(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ITEM_READ)),
    skip: int = 0,
    limit: int = 100
) -> List[InventoryItemResponse]:
    """List inventory items"""
    items = InventoryItemCRUD.get_multi(
        db, company_id=current_user.company_id, skip=skip, limit=limit
    )
    return items


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ITEM_READ)),
    item_id: int
) -> InventoryItemResponse:
    """Get single inventory item by ID"""
    item = InventoryItemCRUD.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if item belongs to user's company
    if item.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return item


@router.post("/items", response_model=InventoryItemResponse)
def create_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ITEM_CREATE)),
    item_data: InventoryItemCreate
) -> InventoryItemResponse:
    """Create new inventory item"""
    
    # Check if item code already exists
    existing_item = InventoryItemCRUD.get_by_code(
        db, company_id=current_user.company_id, item_code=item_data.item_code
    )
    if existing_item:
        raise HTTPException(
            status_code=400, 
            detail=f"Item with code '{item_data.item_code}' already exists"
        )
    
    # Validate GL accounts exist and belong to the company
    if item_data.gl_account_inventory_id:
        asset_account = db.query(GLAccount).filter(
            GLAccount.id == item_data.gl_account_inventory_id,
            GLAccount.company_id == current_user.company_id
        ).first()
        if not asset_account:
            raise HTTPException(status_code=400, detail="Invalid inventory asset account")
    
    if item_data.gl_account_cogs_id:
        expense_account = db.query(GLAccount).filter(
            GLAccount.id == item_data.gl_account_cogs_id,
            GLAccount.company_id == current_user.company_id
        ).first()
        if not expense_account:
            raise HTTPException(status_code=400, detail="Invalid COGS account")
    
    if item_data.gl_account_sales_id:
        revenue_account = db.query(GLAccount).filter(
            GLAccount.id == item_data.gl_account_sales_id,
            GLAccount.company_id == current_user.company_id
        ).first()
        if not revenue_account:
            raise HTTPException(status_code=400, detail="Invalid sales account")
    
    # Set company_id from current user
    item_data.company_id = current_user.company_id
    
    # Create the item
    item = InventoryItemCRUD.create(db, obj_in=item_data)
    return item


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ITEM_UPDATE)),
    item_id: int,
    item_data: InventoryItemUpdate
) -> InventoryItemResponse:
    """Update inventory item"""
    item = InventoryItemCRUD.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if item belongs to user's company
    if item.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate GL accounts if provided
    if item_data.gl_account_inventory_id:
        asset_account = db.query(GLAccount).filter(
            GLAccount.id == item_data.gl_account_inventory_id,
            GLAccount.company_id == current_user.company_id
        ).first()
        if not asset_account:
            raise HTTPException(status_code=400, detail="Invalid inventory asset account")
    
    if item_data.gl_account_cogs_id:
        expense_account = db.query(GLAccount).filter(
            GLAccount.id == item_data.gl_account_cogs_id,
            GLAccount.company_id == current_user.company_id
        ).first()
        if not expense_account:
            raise HTTPException(status_code=400, detail="Invalid COGS account")
    
    if item_data.gl_account_sales_id:
        revenue_account = db.query(GLAccount).filter(
            GLAccount.id == item_data.gl_account_sales_id,
            GLAccount.company_id == current_user.company_id
        ).first()
        if not revenue_account:
            raise HTTPException(status_code=400, detail="Invalid sales account")
    
    # Update the item
    updated_item = InventoryItemCRUD.update(db, db_obj=item, obj_in=item_data)
    return updated_item


@router.delete("/items/{item_id}")
def delete_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ITEM_DELETE)),
    item_id: int
):
    """Delete inventory item"""
    item = InventoryItemCRUD.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if item belongs to user's company
    if item.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if item has transactions (should prevent deletion)
    if item.transactions:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete item with existing transactions"
        )
    
    # Soft delete by setting is_active to False
    item_data = InventoryItemUpdate(is_active=False)
    updated_item = InventoryItemCRUD.update(db, db_obj=item, obj_in=item_data)
    return {"message": "Inventory item deactivated successfully"}


# Transaction Type Endpoints
@router.get("/transaction-types", response_model=List[InventoryTransactionTypeResponse])
def list_transaction_types(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_TRANSACTION_TYPE_READ)),
    skip: int = 0,
    limit: int = 100
) -> List[InventoryTransactionTypeResponse]:
    """List inventory transaction types"""
    transaction_types = InventoryTransactionTypeCRUD.get_multi(
        db, company_id=current_user.company_id, skip=skip, limit=limit
    )
    return transaction_types


@router.get("/transaction-types/{type_id}", response_model=InventoryTransactionTypeResponse)
def get_transaction_type(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_TRANSACTION_TYPE_READ)),
    type_id: int
) -> InventoryTransactionTypeResponse:
    """Get single transaction type by ID"""
    transaction_type = InventoryTransactionTypeCRUD.get(db, id=type_id)
    if not transaction_type:
        raise HTTPException(status_code=404, detail="Transaction type not found")
    
    # Check if transaction type belongs to user's company
    if transaction_type.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return transaction_type


# Transaction Endpoints
# Transaction Endpoints

# === Inventory Adjustments Endpoints ===
@router.get("/adjustments", response_model=List[InventoryTransactionResponse])
def list_inventory_adjustments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ADJUSTMENT_READ)),
    skip: int = 0,
    limit: int = 100
) -> List[InventoryTransactionResponse]:
    """List inventory adjustments (transactions) for the current company"""
    return InventoryTransactionCRUD.get_multi(
        db, company_id=current_user.company_id, skip=skip, limit=limit
    )


@router.post("/adjustments", response_model=InventoryTransactionResponse)
def create_inventory_adjustment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_ADJUSTMENT_CREATE)),
    adjustment_in: InventoryTransactionCreate
) -> InventoryTransactionResponse:
    """Create a new inventory adjustment (transaction)"""
    # Ensure the adjustment is for the current company
    if adjustment_in.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Invalid company context")
    return InventoryTransactionCRUD.create(db, obj_in=adjustment_in)


# Reports Endpoints
@router.get("/reports/stock-levels", response_model=List[dict])
def get_stock_levels_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.INV_REPORT_VIEW)),
    as_at_date: Optional[date] = Query(None)
) -> List[dict]:
    """Get stock levels report - simplified version"""
    return []
