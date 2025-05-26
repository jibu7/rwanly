from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from app.database.database import get_db
from app.core.permissions import Permissions
from app.api.auth import require_permission
from app.models.core import User
from app.schemas.core import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    APTransactionTypeCreate, APTransactionTypeUpdate, APTransactionTypeResponse,
    APTransactionCreate, APTransactionUpdate, APTransactionResponse,
    APAllocationCreate, APAllocationResponse
)
from app.crud.accounts_payable import (
    supplier_crud, ap_transaction_type_crud, ap_transaction_crud, ap_allocation_crud
)
from fastapi import Depends

router = APIRouter()

# Supplier Endpoints
@router.post("/suppliers/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: SupplierCreate, current_user: User = Depends(require_permission(Permissions.AP_CREATE_SUPPLIERS)), db: Session = Depends(get_db)):
    supplier.company_id = current_user.company_id
    return supplier_crud.create_supplier(db, supplier)

@router.get("/suppliers/", response_model=List[SupplierResponse])
def list_suppliers(is_active: Optional[bool] = Query(None), current_user: User = Depends(require_permission(Permissions.AP_VIEW_SUPPLIERS)), db: Session = Depends(get_db)):
    return supplier_crud.get_suppliers(db, current_user.company_id, is_active)

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, current_user: User = Depends(require_permission(Permissions.AP_VIEW_SUPPLIERS)), db: Session = Depends(get_db)):
    supplier = supplier_crud.get_supplier(db, supplier_id, current_user.company_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier_update: SupplierUpdate, current_user: User = Depends(require_permission(Permissions.AP_EDIT_SUPPLIERS)), db: Session = Depends(get_db)):
    supplier = supplier_crud.update_supplier(db, supplier_id, current_user.company_id, supplier_update)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, current_user: User = Depends(require_permission(Permissions.AP_DELETE_SUPPLIERS)), db: Session = Depends(get_db)):
    success = supplier_crud.delete_supplier(db, supplier_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return

# AP Transaction Type Endpoints
@router.post("/transaction-types/", response_model=APTransactionTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ap_transaction_type(transaction_type: APTransactionTypeCreate, current_user: User = Depends(require_permission(Permissions.AP_CREATE_TRANSACTION_TYPES)), db: Session = Depends(get_db)):
    transaction_type.company_id = current_user.company_id
    return ap_transaction_type_crud.create_transaction_type(db, transaction_type)

@router.get("/transaction-types/", response_model=List[APTransactionTypeResponse])
def list_ap_transaction_types(is_active: Optional[bool] = Query(None), current_user: User = Depends(require_permission(Permissions.AP_VIEW_TRANSACTION_TYPES)), db: Session = Depends(get_db)):
    return ap_transaction_type_crud.get_transaction_types(db, current_user.company_id, is_active)

@router.get("/transaction-types/{type_id}", response_model=APTransactionTypeResponse)
def get_ap_transaction_type(type_id: int, current_user: User = Depends(require_permission(Permissions.AP_VIEW_TRANSACTION_TYPES)), db: Session = Depends(get_db)):
    transaction_type = ap_transaction_type_crud.get_transaction_type(db, type_id, current_user.company_id)
    if not transaction_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction type not found")
    return transaction_type

@router.put("/transaction-types/{type_id}", response_model=APTransactionTypeResponse)
def update_ap_transaction_type(type_id: int, type_update: APTransactionTypeUpdate, current_user: User = Depends(require_permission(Permissions.AP_EDIT_TRANSACTION_TYPES)), db: Session = Depends(get_db)):
    transaction_type = ap_transaction_type_crud.update_transaction_type(db, type_id, current_user.company_id, type_update)
    if not transaction_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction type not found")
    return transaction_type

# AP Transaction Endpoints
@router.post("/transactions/", response_model=APTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_ap_transaction(transaction: APTransactionCreate, current_user: User = Depends(require_permission(Permissions.AP_CREATE_TRANSACTIONS)), db: Session = Depends(get_db)):
    transaction.company_id = current_user.company_id
    return ap_transaction_crud.create_transaction(db, transaction)

@router.get("/transactions/", response_model=List[APTransactionResponse])
def list_ap_transactions(supplier_id: Optional[int] = Query(None), transaction_type_id: Optional[int] = Query(None), date_from: Optional[date] = Query(None), date_to: Optional[date] = Query(None), is_posted: Optional[bool] = Query(None), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), current_user: User = Depends(require_permission(Permissions.AP_VIEW_TRANSACTIONS)), db: Session = Depends(get_db)):
    return ap_transaction_crud.get_transactions(db, current_user.company_id, supplier_id, transaction_type_id, date_from, date_to, is_posted, skip, limit)

@router.get("/transactions/{transaction_id}", response_model=APTransactionResponse)
def get_ap_transaction(transaction_id: int, current_user: User = Depends(require_permission(Permissions.AP_VIEW_TRANSACTIONS)), db: Session = Depends(get_db)):
    transaction = ap_transaction_crud.get_transaction(db, transaction_id, current_user.company_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction

@router.put("/transactions/{transaction_id}", response_model=APTransactionResponse)
def update_ap_transaction(transaction_id: int, transaction_update: APTransactionUpdate, current_user: User = Depends(require_permission(Permissions.AP_EDIT_TRANSACTIONS)), db: Session = Depends(get_db)):
    try:
        transaction = ap_transaction_crud.update_transaction(db, transaction_id, current_user.company_id, transaction_update)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/transactions/{transaction_id}/post", response_model=APTransactionResponse)
def post_ap_transaction(transaction_id: int, current_user: User = Depends(require_permission(Permissions.AP_POST_TRANSACTIONS)), db: Session = Depends(get_db)):
    try:
        transaction = ap_transaction_crud.post_transaction(db, transaction_id, current_user.company_id, current_user.id)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# AP Allocation Endpoints
@router.post("/allocations/", response_model=APAllocationResponse, status_code=status.HTTP_201_CREATED)
def create_ap_allocation(allocation: APAllocationCreate, current_user: User = Depends(require_permission(Permissions.AP_ALLOCATE_PAYMENTS)), db: Session = Depends(get_db)):
    allocation.company_id = current_user.company_id
    return ap_allocation_crud.create_allocation(db, allocation, posted_by=current_user.id)

@router.get("/allocations/", response_model=List[APAllocationResponse])
def list_ap_allocations(supplier_id: Optional[int] = Query(None), current_user: User = Depends(require_permission(Permissions.AP_VIEW_ALLOCATIONS)), db: Session = Depends(get_db)):
    return ap_allocation_crud.get_allocations(db, current_user.company_id, supplier_id)
