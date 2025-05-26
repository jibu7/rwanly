from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database.database import get_db
from app.api.auth import get_current_user, require_permission
from app.core.permissions import Permissions
from app.models.core import User
from app.schemas.core import (
    GLAccountCreateRequest, GLAccountUpdate, GLAccountResponse,
    GLTransactionCreateRequest, GLTransactionUpdate, GLTransactionResponse,
    ChartOfAccountsResponse, TrialBalanceResponse, TrialBalanceItem
)
from app.crud.general_ledger import gl_account_crud, gl_transaction_crud
from app.crud.core import accounting_period_crud

router = APIRouter()


# GL Account Endpoints
@router.post("/accounts", response_model=GLAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_gl_account(
    account: GLAccountCreateRequest,
    current_user: User = Depends(require_permission(Permissions.GL_ACCOUNT_CREATE)),
    db: Session = Depends(get_db)
):
    """Create a new General Ledger account - REQ-GL-COA-CREATE"""
    # Check if account code already exists
    existing_account = gl_account_crud.get_account_by_code(db, account.account_code, current_user.company_id)
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account code already exists"
        )
    
    # Create account with company_id from current user
    account_data = account.model_dump()
    account_data["company_id"] = current_user.company_id
    
    from app.schemas.core import GLAccountCreate
    account_create = GLAccountCreate(**account_data)
    
    try:
        return gl_account_crud.create_account(db, account_create)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/accounts", response_model=List[GLAccountResponse])
async def get_gl_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_type: Optional[str] = Query(None, pattern="^(ASSETS|LIABILITIES|EQUITY|REVENUE|EXPENSES)$"),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission(Permissions.GL_ACCOUNT_READ)),
    db: Session = Depends(get_db)
):
    """Get General Ledger accounts - REQ-GL-COA-READ"""
    return gl_account_crud.get_accounts(
        db, current_user.company_id, skip, limit, account_type, is_active
    )


@router.get("/accounts/chart", response_model=ChartOfAccountsResponse)
async def get_chart_of_accounts(
    current_user: User = Depends(require_permission(Permissions.GL_ACCOUNT_READ)),
    db: Session = Depends(get_db)
):
    """Get the complete Chart of Accounts - REQ-GL-COA-CHART"""
    accounts = gl_account_crud.get_accounts(db, current_user.company_id, skip=0, limit=10000, is_active=True)
    return ChartOfAccountsResponse(accounts=accounts)


@router.get("/accounts/{account_id}", response_model=GLAccountResponse)
async def get_gl_account(
    account_id: int,
    current_user: User = Depends(require_permission(Permissions.GL_ACCOUNT_READ)),
    db: Session = Depends(get_db)
):
    """Get a specific General Ledger account - REQ-GL-COA-READ"""
    account = gl_account_crud.get_account(db, account_id, current_user.company_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GL Account not found"
        )
    return account


@router.put("/accounts/{account_id}", response_model=GLAccountResponse)
async def update_gl_account(
    account_id: int,
    account_update: GLAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a General Ledger account - REQ-GL-COA-UPDATE"""
    require_permission(current_user, "gl_account_update")
    
    account = gl_account_crud.update_account(db, account_id, current_user.company_id, account_update)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GL Account not found"
        )
    return account


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gl_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a General Ledger account - REQ-GL-COA-DELETE"""
    require_permission(current_user, "gl_account_delete")
    
    success = gl_account_crud.delete_account(db, account_id, current_user.company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GL Account not found"
        )


# GL Transaction Endpoints
@router.post("/transactions", response_model=GLTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_gl_transaction(
    transaction: GLTransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new General Ledger transaction - REQ-GL-TRANS-CREATE"""
    require_permission(current_user, "gl_transaction_create")
    
    # Validate that the GL account exists and belongs to the company
    account = gl_account_crud.get_account(db, transaction.gl_account_id, current_user.company_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GL Account not found"
        )
    
    # Validate that the accounting period exists and belongs to the company
    period = accounting_period_crud.get_period(db, transaction.accounting_period_id, current_user.company_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    # Check if the accounting period is closed
    if period.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create transactions in a closed accounting period"
        )
    
    # Create transaction with company_id and posted_by from current user
    transaction_data = transaction.model_dump()
    transaction_data["company_id"] = current_user.company_id
    transaction_data["posted_by"] = current_user.id
    
    from app.schemas.core import GLTransactionCreate
    transaction_create = GLTransactionCreate(**transaction_data)
    
    try:
        return gl_transaction_crud.create_transaction(db, transaction_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/transactions", response_model=List[GLTransactionResponse])
async def get_gl_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = Query(None),
    period_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get General Ledger transactions - REQ-GL-TRANS-READ"""
    require_permission(current_user, "gl_transaction_read")
    
    return gl_transaction_crud.get_transactions(
        db, current_user.company_id, skip, limit, account_id, period_id, start_date, end_date
    )


@router.get("/transactions/{transaction_id}", response_model=GLTransactionResponse)
async def get_gl_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific General Ledger transaction - REQ-GL-TRANS-READ"""
    require_permission(current_user, "gl_transaction_read")
    
    transaction = gl_transaction_crud.get_transaction(db, transaction_id, current_user.company_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GL Transaction not found"
        )
    return transaction


@router.put("/transactions/{transaction_id}", response_model=GLTransactionResponse)
async def update_gl_transaction(
    transaction_id: int,
    transaction_update: GLTransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a General Ledger transaction - REQ-GL-TRANS-UPDATE"""
    require_permission(current_user, "gl_transaction_update")
    
    try:
        transaction = gl_transaction_crud.update_transaction(db, transaction_id, current_user.company_id, transaction_update)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GL Transaction not found"
            )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gl_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a General Ledger transaction - REQ-GL-TRANS-DELETE"""
    require_permission(current_user, "gl_transaction_delete")
    
    try:
        success = gl_transaction_crud.delete_transaction(db, transaction_id, current_user.company_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GL Transaction not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Reporting Endpoints
@router.get("/reports/trial-balance/{period_id}", response_model=TrialBalanceResponse)
async def get_trial_balance(
    period_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate Trial Balance report - REQ-GL-REPORT-TB"""
    require_permission(current_user, "gl_reports_read")
    
    # Get the accounting period
    period = accounting_period_crud.get_period(db, period_id, current_user.company_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    try:
        trial_balance_items = gl_transaction_crud.get_trial_balance(db, current_user.company_id, period_id)
        
        # Calculate totals
        total_debits = sum(item.debit_balance for item in trial_balance_items)
        total_credits = sum(item.credit_balance for item in trial_balance_items)
        is_balanced = abs(total_debits - total_credits) < 0.01  # Allow for small rounding differences
        
        return TrialBalanceResponse(
            period_id=period_id,
            period_name=period.period_name,
            as_of_date=period.end_date,
            accounts=trial_balance_items,
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=is_balanced
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
