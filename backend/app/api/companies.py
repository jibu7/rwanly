from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CompanyResponse, CompanyCreate, CompanyUpdate
from app.crud import company_crud
from app.core.permissions import Permissions
from app.api.auth import get_current_active_user, require_permission
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all companies (admin only)"""
    # Check if user has SYS_COMPANY_READ permission
    user_permissions = []
    for user_role in current_user.user_roles:
        role_permissions = user_role.role.permissions or []
        user_permissions.extend(role_permissions)
    
    if not (Permissions.SYS_COMPANY_READ in user_permissions or "all" in user_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    companies = company_crud.get_all(db, skip=skip, limit=limit)
    return companies


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(require_permission(Permissions.SYS_COMPANY_CREATE)),
    db: Session = Depends(get_db)
):
    """Create a new company"""
    return company_crud.create(db, company_data)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_COMPANY_READ)),
    db: Session = Depends(get_db)
):
    """Get a specific company"""
    company = company_crud.get_by_id(db, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(require_permission(Permissions.SYS_COMPANY_UPDATE)),
    db: Session = Depends(get_db)
):
    """Update a company"""
    company = company_crud.get_by_id(db, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    updated_company = company_crud.update(db, company_id=company_id, company_data=company_data)
    return updated_company
