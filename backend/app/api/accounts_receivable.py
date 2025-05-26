from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.api.auth import get_current_active_user, require_permission
from app.models import User
from app.schemas.core import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    ARTransactionTypeCreate, ARTransactionTypeUpdate, ARTransactionTypeResponse,
    ARTransactionCreate, ARTransactionUpdate, ARTransactionResponse,
    ARAllocationCreate, ARAllocationResponse,
    AgeingPeriodCreate, AgeingPeriodUpdate, AgeingPeriodResponse,
    CustomerAgeingReport, CustomerTransactionReport
)
from app.crud.accounts_receivable import (
    customer_crud, ar_transaction_type_crud, ar_transaction_crud,
    ar_allocation_crud, ageing_period_crud, ar_reporting_crud
)
from app.core.permissions import Permissions

router = APIRouter()

# ================================
# CUSTOMER ENDPOINTS (REQ-AR-CUST-*)
# ================================

@router.get("/customers/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_CUSTOMERS)),
    db: Session = Depends(get_db)
):
    """List customers - REQ-AR-CUST-001"""
    customers = customer_crud.get_customers(
        db, 
        company_id=current_user.company_id,
        skip=skip, 
        limit=limit,
        is_active=is_active,
        search=search
    )
    return customers


@router.post("/customers/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(require_permission(Permissions.AR_CREATE_CUSTOMERS)),
    db: Session = Depends(get_db)
):
    """Create a new customer - REQ-AR-CUST-001"""
    # Set company_id from current user
    customer.company_id = current_user.company_id
    
    # Check if customer code already exists
    existing = customer_crud.get_customer_by_code(db, customer.customer_code, customer.company_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer code already exists"
        )
    
    return customer_crud.create_customer(db, customer)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_CUSTOMERS)),
    db: Session = Depends(get_db)
):
    """Get a specific customer - REQ-AR-CUST-001"""
    customer = customer_crud.get_customer(db, customer_id, current_user.company_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(require_permission(Permissions.AR_EDIT_CUSTOMERS)),
    db: Session = Depends(get_db)
):
    """Update a customer - REQ-AR-CUST-001"""
    customer = customer_crud.update_customer(db, customer_id, current_user.company_id, customer_update)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_permission(Permissions.AR_DELETE_CUSTOMERS)),
    db: Session = Depends(get_db)
):
    """Delete a customer (soft delete) - REQ-AR-CUST-001"""
    success = customer_crud.delete_customer(db, customer_id, current_user.company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )


# ================================
# AR TRANSACTION TYPE ENDPOINTS (REQ-AR-TT-*)
# ================================

@router.get("/transaction-types/", response_model=List[ARTransactionTypeResponse])
async def list_ar_transaction_types(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_TRANSACTION_TYPES)),
    db: Session = Depends(get_db)
):
    """List AR transaction types - REQ-AR-TT-001"""
    return ar_transaction_type_crud.get_transaction_types(
        db, current_user.company_id, is_active=is_active
    )


@router.post("/transaction-types/", response_model=ARTransactionTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_ar_transaction_type(
    transaction_type: ARTransactionTypeCreate,
    current_user: User = Depends(require_permission(Permissions.AR_CREATE_TRANSACTION_TYPES)),
    db: Session = Depends(get_db)
):
    """Create a new AR transaction type - REQ-AR-TT-001"""
    transaction_type.company_id = current_user.company_id
    
    # Check if type code already exists
    existing = ar_transaction_type_crud.get_transaction_type_by_code(
        db, transaction_type.type_code, transaction_type.company_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type code already exists"
        )
    
    return ar_transaction_type_crud.create_transaction_type(db, transaction_type)


@router.get("/transaction-types/{type_id}", response_model=ARTransactionTypeResponse)
async def get_ar_transaction_type(
    type_id: int,
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_TRANSACTION_TYPES)),
    db: Session = Depends(get_db)
):
    """Get a specific AR transaction type - REQ-AR-TT-001"""
    transaction_type = ar_transaction_type_crud.get_transaction_type(db, type_id, current_user.company_id)
    if not transaction_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction type not found"
        )
    return transaction_type


@router.put("/transaction-types/{type_id}", response_model=ARTransactionTypeResponse)
async def update_ar_transaction_type(
    type_id: int,
    type_update: ARTransactionTypeUpdate,
    current_user: User = Depends(require_permission(Permissions.AR_EDIT_TRANSACTION_TYPES)),
    db: Session = Depends(get_db)
):
    """Update an AR transaction type - REQ-AR-TT-002"""
    transaction_type = ar_transaction_type_crud.update_transaction_type(
        db, type_id, current_user.company_id, type_update
    )
    if not transaction_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction type not found"
        )
    return transaction_type


# ================================
# AR TRANSACTION ENDPOINTS (REQ-AR-TP-*)
# ================================

@router.get("/transactions/", response_model=List[ARTransactionResponse])
async def list_ar_transactions(
    customer_id: Optional[int] = Query(None),
    transaction_type_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    is_posted: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_TRANSACTIONS)),
    db: Session = Depends(get_db)
):
    """List AR transactions - REQ-AR-TP-001"""
    transactions = ar_transaction_crud.get_transactions(
        db,
        company_id=current_user.company_id,
        customer_id=customer_id,
        transaction_type_id=transaction_type_id,
        date_from=date_from,
        date_to=date_to,
        is_posted=is_posted,
        skip=skip,
        limit=limit
    )
    return transactions


@router.post("/transactions/", response_model=ARTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_ar_transaction(
    transaction: ARTransactionCreate,
    current_user: User = Depends(require_permission(Permissions.AR_CREATE_TRANSACTIONS)),
    db: Session = Depends(get_db)
):
    """Create a new AR transaction - REQ-AR-TP-001"""
    transaction.company_id = current_user.company_id
    return ar_transaction_crud.create_transaction(db, transaction)


@router.get("/transactions/{transaction_id}", response_model=ARTransactionResponse)
async def get_ar_transaction(
    transaction_id: int,
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_TRANSACTIONS)),
    db: Session = Depends(get_db)
):
    """Get a specific AR transaction - REQ-AR-TP-001"""
    transaction = ar_transaction_crud.get_transaction(db, transaction_id, current_user.company_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction


@router.put("/transactions/{transaction_id}", response_model=ARTransactionResponse)
async def update_ar_transaction(
    transaction_id: int,
    transaction_update: ARTransactionUpdate,
    current_user: User = Depends(require_permission(Permissions.AR_EDIT_TRANSACTIONS)),
    db: Session = Depends(get_db)
):
    """Update an AR transaction - REQ-AR-TP-001"""
    try:
        transaction = ar_transaction_crud.update_transaction(
            db, transaction_id, current_user.company_id, transaction_update
        )
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/transactions/{transaction_id}/post", response_model=ARTransactionResponse)
async def post_ar_transaction(
    transaction_id: int,
    current_user: User = Depends(require_permission(Permissions.AR_POST_TRANSACTIONS)),
    db: Session = Depends(get_db)
):
    """Post an AR transaction to GL - REQ-AR-TP-002"""
    try:
        transaction = ar_transaction_crud.post_transaction(
            db, transaction_id, current_user.company_id, current_user.id
        )
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/transactions/outstanding/invoices", response_model=List[ARTransactionResponse])
async def get_outstanding_invoices(
    customer_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_TRANSACTIONS)),
    db: Session = Depends(get_db)
):
    """Get outstanding invoices for allocation - REQ-AR-ALLOC-001"""
    return ar_transaction_crud.get_outstanding_invoices(
        db, current_user.company_id, customer_id=customer_id
    )


# ================================
# AR ALLOCATION ENDPOINTS (REQ-AR-ALLOC-*)
# ================================

@router.post("/allocations/", response_model=ARAllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_ar_allocation(
    allocation: ARAllocationCreate,
    current_user: User = Depends(require_permission(Permissions.AR_CREATE_ALLOCATIONS)),
    db: Session = Depends(get_db)
):
    """Create a new AR allocation - REQ-AR-ALLOC-001"""
    allocation.company_id = current_user.company_id
    
    try:
        return ar_allocation_crud.create_allocation(db, allocation, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/allocations/", response_model=List[ARAllocationResponse])
async def list_ar_allocations(
    customer_id: Optional[int] = Query(None),
    transaction_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_ALLOCATIONS)),
    db: Session = Depends(get_db)
):
    """List AR allocations - REQ-AR-ALLOC-002"""
    return ar_allocation_crud.get_allocations(
        db, current_user.company_id, customer_id=customer_id, transaction_id=transaction_id
    )


# ================================
# AGEING PERIOD ENDPOINTS (REQ-AR-AGE-*)
# ================================

@router.get("/ageing-periods/", response_model=List[AgeingPeriodResponse])
async def list_ageing_periods(
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_AGEING)),
    db: Session = Depends(get_db)
):
    """List ageing periods - REQ-AR-AGE-001"""
    return ageing_period_crud.get_ageing_periods(db, current_user.company_id)


@router.post("/ageing-periods/", response_model=List[AgeingPeriodResponse], status_code=status.HTTP_201_CREATED)
async def setup_default_ageing_periods(
    current_user: User = Depends(require_permission(Permissions.AR_SETUP_AGEING)),
    db: Session = Depends(get_db)
):
    """Setup default ageing periods - REQ-AR-AGE-001"""
    return ageing_period_crud.setup_default_ageing_periods(db, current_user.company_id)


# ================================
# AR REPORTING ENDPOINTS (REQ-AR-REPORT-*)
# ================================

@router.get("/reports/customer-ageing", response_model=CustomerAgeingReport)
async def generate_customer_ageing_report(
    as_at_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_REPORTS)),
    db: Session = Depends(get_db)
):
    """Generate customer ageing report - REQ-AR-REPORT-001"""
    return ar_reporting_crud.generate_customer_ageing_report(
        db, current_user.company_id, as_at_date=as_at_date
    )


@router.get("/reports/customer-transactions/{customer_id}", response_model=CustomerTransactionReport)
async def generate_customer_transaction_report(
    customer_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_REPORTS)),
    db: Session = Depends(get_db)
):
    """Generate customer transaction report - REQ-AR-REPORT-003"""
    try:
        return ar_reporting_crud.generate_customer_transaction_report(
            db, current_user.company_id, customer_id, date_from=date_from, date_to=date_to
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/reports/customer-listing", response_model=List[CustomerResponse])
async def generate_customer_listing_report(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission(Permissions.AR_VIEW_REPORTS)),
    db: Session = Depends(get_db)
):
    """Generate customer listing report - REQ-AR-REPORT-002"""
    return customer_crud.get_customers(
        db, current_user.company_id, is_active=is_active, skip=0, limit=10000
    )
