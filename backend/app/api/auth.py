from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.database import get_db
from app.schemas import UserResponse, UserCreate, UserUpdate, Token, LoginRequest
from app.crud.core import user_crud
from app.core.security import verify_password, create_access_token, verify_token
from app.core.permissions import check_permission, Permissions
from app.models.core import User

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from token"""
    token_data = verify_token(token)
    user = user_crud.get_by_username(db, username=token_data["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: str):
    """Dependency factory for checking permissions"""
    def permission_checker(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
        # Get user's permissions from their roles
        user_permissions = []
        for user_role in current_user.user_roles:
            role_permissions = user_role.role.permissions or []
            user_permissions.extend(role_permissions)
        
        if not check_permission(user_permissions, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    
    return permission_checker


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    # Allow login by either username or email
    user = user_crud.get_by_username(db, username=form_data.username)
    if not user:
        user = user_crud.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=30)  # You can configure this
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get current user information with permissions"""
    # Collect all permissions from user's roles
    permission_strings = []
    for user_role in current_user.user_roles:
        role_permissions = user_role.role.permissions or []
        permission_strings.extend(role_permissions)
    
    # Remove duplicates
    permission_strings = list(set(permission_strings))
    
    # Convert backend permission strings to frontend Permission objects
    permissions = []
    for perm_str in permission_strings:
        frontend_resource = None
        action = None
        
        if ':' in perm_str:
            parts = perm_str.split(':')
            if len(parts) >= 3:
                module = parts[0]
                resource = parts[1] 
                action = parts[2]
                
                # Map specific backend permissions to frontend resources
                if module == 'inv' or resource.startswith('inventory'):
                    frontend_resource = 'inventory'
                elif module == 'gl' or module == 'general_ledger':
                    frontend_resource = 'general_ledger'
                elif module == 'ar' or module == 'accounts_receivable':
                    frontend_resource = 'accounts_receivable'
                elif module == 'ap' or module == 'accounts_payable':
                    frontend_resource = 'accounts_payable'
                elif module == 'oe' or module == 'order_entry':
                    frontend_resource = 'order_entry'
                elif module == 'sys':
                    if resource == 'user':
                        frontend_resource = 'users'
                    elif resource == 'role':
                        frontend_resource = 'roles'
                    elif resource == 'company':
                        frontend_resource = 'companies'
                    elif resource == 'accounting_period':
                        frontend_resource = 'accounting_periods'
        
        # Handle permissions with underscore format like "inventory_items:read"
        elif '_' in perm_str and ':' in perm_str:
            parts = perm_str.split(':')
            if len(parts) >= 2:
                resource_part = parts[0]
                action = parts[1]
                
                if resource_part.startswith('inventory'):
                    frontend_resource = 'inventory'
                elif resource_part.startswith('gl') or resource_part == 'general_ledger':
                    frontend_resource = 'general_ledger'
                elif resource_part.startswith('ar') or resource_part == 'accounts_receivable':
                    frontend_resource = 'accounts_receivable'
                elif resource_part.startswith('ap') or resource_part == 'accounts_payable':
                    frontend_resource = 'accounts_payable'
                    
        # Special case for admin - always add inventory read permission if they have any inventory permission
        if any('inventory' in p for p in permission_strings) and current_user.user_roles and current_user.user_roles[0].role.name == 'Administrator':
            permissions.append({"resource": "inventory", "action": "read"})
        
        if frontend_resource and action:
            permissions.append({
                "resource": frontend_resource,
                "action": action
            })
    
    # Remove duplicate permissions
    seen = set()
    unique_permissions = []
    for perm in permissions:
        perm_tuple = (perm["resource"], perm["action"])
        if perm_tuple not in seen:
            seen.add(perm_tuple)
            unique_permissions.append(perm)
    
    # Get primary role name
    primary_role = None
    if current_user.user_roles:
        primary_role = current_user.user_roles[0].role.name
    
    # Create display name
    name = None
    if current_user.first_name or current_user.last_name:
        name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
    
    # Create response with permissions
    response_data = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "company_id": current_user.company_id,
        "created_at": current_user.created_at,
        "permissions": unique_permissions,
        "permission_strings": permission_strings,
        "role": primary_role,
        "name": name
    }
    
    return response_data


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (token invalidation would be handled by frontend)"""
    return {"message": "Successfully logged out"}
