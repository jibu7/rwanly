from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.api.auth import get_current_active_user, require_permission
from app.core.permissions import Permissions
from app.models import User
from app.schemas import AccountingPeriodCreate, AccountingPeriodCreateRequest, AccountingPeriodUpdate, AccountingPeriodResponse
from app.crud import accounting_period_crud

router = APIRouter(prefix="/accounting-periods", tags=["accounting-periods"])


@router.get("/", response_model=List[AccountingPeriodResponse])
async def list_accounting_periods(
    skip: int = 0,
    limit: int = 100,
    financial_year: int = None,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_READ)),
    db: Session = Depends(get_db)
):
    """
    List accounting periods for the current user's company.
    Can filter by financial year.
    """
    if financial_year:
        periods = accounting_period_crud.get_by_financial_year(
            db, current_user.company_id, financial_year
        )
    else:
        periods = accounting_period_crud.get_by_company(
            db, current_user.company_id, skip, limit
        )
    return periods


@router.get("/current", response_model=AccountingPeriodResponse)
async def get_current_period(
    transaction_date: date = None,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_READ)),
    db: Session = Depends(get_db)
):
    """Get the current accounting period for a specific date (defaults to today)."""
    if transaction_date is None:
        transaction_date = date.today()
    
    period = accounting_period_crud.get_current_period(
        db, current_user.company_id, transaction_date
    )
    
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No accounting period found for date {transaction_date}"
        )
    
    return period


@router.get("/open", response_model=List[AccountingPeriodResponse])
async def list_open_periods(
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_READ)),
    db: Session = Depends(get_db)
):
    """List all open (not closed) accounting periods."""
    periods = accounting_period_crud.get_open_periods(db, current_user.company_id)
    return periods


@router.get("/{period_id}", response_model=AccountingPeriodResponse)
async def get_accounting_period(
    period_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_READ)),
    db: Session = Depends(get_db)
):
    """Get a specific accounting period."""
    period = accounting_period_crud.get_by_id(db, period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    # Ensure user can only access periods from their company
    if period.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this accounting period"
        )
    
    return period


@router.post("/", response_model=AccountingPeriodResponse)
async def create_accounting_period(
    period_data: AccountingPeriodCreateRequest,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_CREATE)),
    db: Session = Depends(get_db)
):
    """Create a new accounting period."""
    # Convert to AccountingPeriodCreate and set company_id
    period_create_data = AccountingPeriodCreate(
        **period_data.dict(),
        company_id=current_user.company_id
    )
    
    try:
        period = accounting_period_crud.create(db, period_create_data)
        return period
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{period_id}", response_model=AccountingPeriodResponse)
async def update_accounting_period(
    period_id: int,
    period_data: AccountingPeriodUpdate,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_UPDATE)),
    db: Session = Depends(get_db)
):
    """Update an accounting period."""
    # Check if period exists and belongs to user's company
    existing_period = accounting_period_crud.get_by_id(db, period_id)
    if not existing_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    if existing_period.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this accounting period"
        )
    
    try:
        period = accounting_period_crud.update(db, period_id, period_data)
        return period
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{period_id}/close", response_model=AccountingPeriodResponse)
async def close_accounting_period(
    period_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_CLOSE)),
    db: Session = Depends(get_db)
):
    """Close an accounting period."""
    # Check if period exists and belongs to user's company
    existing_period = accounting_period_crud.get_by_id(db, period_id)
    if not existing_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    if existing_period.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this accounting period"
        )
    
    if existing_period.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accounting period is already closed"
        )
    
    period = accounting_period_crud.close_period(db, period_id)
    return period


@router.post("/{period_id}/reopen", response_model=AccountingPeriodResponse)
async def reopen_accounting_period(
    period_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_REOPEN)),
    db: Session = Depends(get_db)
):
    """Reopen a closed accounting period."""
    # Check if period exists and belongs to user's company
    existing_period = accounting_period_crud.get_by_id(db, period_id)
    if not existing_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    if existing_period.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this accounting period"
        )
    
    if not existing_period.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accounting period is not closed"
        )
    
    period = accounting_period_crud.reopen_period(db, period_id)
    return period


@router.delete("/{period_id}")
async def delete_accounting_period(
    period_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_ACCOUNTING_PERIOD_DELETE)),
    db: Session = Depends(get_db)
):
    """Delete an accounting period (only if no transactions exist)."""
    # Check if period exists and belongs to user's company
    existing_period = accounting_period_crud.get_by_id(db, period_id)
    if not existing_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accounting period not found"
        )
    
    if existing_period.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this accounting period"
        )
    
    # TODO: Add check for existing transactions in this period
    # This will be implemented when transaction models are available
    
    success = accounting_period_crud.delete(db, period_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete accounting period"
        )
    
    return {"message": "Accounting period deleted successfully"}
