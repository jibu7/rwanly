from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RoleResponse, RoleCreate, RoleUpdate
from app.crud import role_crud
from app.core.permissions import Permissions, get_all_permissions
from app.api.auth import get_current_active_user, require_permission
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission(Permissions.SYS_ROLE_READ)),
    db: Session = Depends(get_db)
):
    """Get all roles in the current user's company"""
    roles = role_crud.get_by_company(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return roles


@router.post("/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_permission(Permissions.SYS_ROLE_CREATE)),
    db: Session = Depends(get_db)
):
    """Create a new role"""
    # Ensure role is created in the same company as the current user
    role_data.company_id = current_user.company_id
    
    # Validate permissions
    all_permissions = get_all_permissions()
    invalid_permissions = [p for p in role_data.permissions if p not in all_permissions]
    if invalid_permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permissions: {invalid_permissions}"
        )
    
    return role_crud.create(db, role_data)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_ROLE_READ)),
    db: Session = Depends(get_db)
):
    """Get a specific role"""
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Ensure role belongs to the same company
    if role.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permission(Permissions.SYS_ROLE_UPDATE)),
    db: Session = Depends(get_db)
):
    """Update a role"""
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Ensure role belongs to the same company
    if role.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Validate permissions if provided
    if role_data.permissions is not None:
        all_permissions = get_all_permissions()
        invalid_permissions = [p for p in role_data.permissions if p not in all_permissions]
        if invalid_permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permissions: {invalid_permissions}"
            )
    
    updated_role = role_crud.update(db, role_id=role_id, role_data=role_data)
    return updated_role


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_ROLE_DELETE)),
    db: Session = Depends(get_db)
):
    """Delete a role"""
    role = role_crud.get_by_id(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Ensure role belongs to the same company
    if role.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    success = role_crud.delete(db, role_id=role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete role"
        )
    
    return {"message": "Role deleted successfully"}


@router.get("/permissions/all")
async def get_all_available_permissions(
    current_user: User = Depends(require_permission(Permissions.SYS_ROLE_READ))
):
    """Get all available permissions in the system"""
    return {"permissions": get_all_permissions()}
