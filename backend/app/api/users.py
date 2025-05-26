from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserResponse, UserCreate, UserUpdate
from app.crud import user_crud
from app.core.permissions import Permissions
from app.api.auth import get_current_active_user, require_permission
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission(Permissions.SYS_USER_READ)),
    db: Session = Depends(get_db)
):
    """Get all users in the current user's company"""
    users = user_crud.get_by_company(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission(Permissions.SYS_USER_CREATE)),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    # Check if username already exists
    if user_crud.get_by_username(db, username=user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_crud.get_by_email(db, email=user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Ensure user is created in the same company as the current user
    user_data.company_id = current_user.company_id
    
    return user_crud.create(db, user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_USER_READ)),
    db: Session = Depends(get_db)
):
    """Get a specific user"""
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure user belongs to the same company
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_permission(Permissions.SYS_USER_UPDATE)),
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure user belongs to the same company
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    updated_user = user_crud.update(db, user_id=user_id, user_data=user_data)
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_USER_DELETE)),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure user belongs to the same company
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Prevent users from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_crud.delete(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user"
        )
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/assign-role")
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_permission(Permissions.SYS_USER_UPDATE)),
    db: Session = Depends(get_db)
):
    """Assign a role to a user"""
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure user belongs to the same company
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    success = user_crud.assign_role(db, user_id=user_id, role_id=role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already assigned or role not found"
        )
    
    return {"message": "Role assigned successfully"}
