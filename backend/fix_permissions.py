#!/usr/bin/env python3
"""
Script to fix the permission checking function in the backend.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.database.database import engine, SessionLocal
from app.models.core import Role, User, UserRole
from app.core.permissions import Permissions

# Fix the check_permission function to handle both formats
def fix_permission_checker():
    """Fix the permission checking function"""
    
    # Read the current permissions.py file
    permissions_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "app", "core", "permissions.py")
    
    with open(permissions_file, "r") as f:
        content = f.read()
    
    # Find the check_permission function and replace it
    old_function = """def check_permission(user_permissions: List[str], required_permission: str) -> bool:
    \"\"\"Check if user has the required permission\"\"\"
    # Check for exact permission match
    if required_permission in user_permissions:
        return True
    
    # Check for "all" permission (admin wildcard)
    if "all" in user_permissions:
        return True
    """
    
    new_function = """def check_permission(user_or_permissions, module_or_permission, action=None):
    \"\"\"
    Check if user has the required permission.
    
    This function handles two formats:
    1. check_permission(user, "module", "action") - Used in API modules
    2. check_permission(user_permissions, "module:action") - Used in auth middleware
    
    Args:
        user_or_permissions: Either a User object or a list of permission strings
        module_or_permission: Either a module name or a permission string
        action: Optional action name when using format #1
        
    Returns:
        bool: True if the user has the required permission
    \"\"\"
    user_permissions = []
    
    # Handle user object vs direct permissions list
    if isinstance(user_or_permissions, list):
        user_permissions = user_or_permissions
    else:
        # It's a user object, extract permissions from roles
        user = user_or_permissions
        for user_role in user.user_roles:
            role_permissions = user_role.role.permissions or []
            user_permissions.extend(role_permissions)
    
    # Format the required permission based on which signature was used
    required_permission = None
    if action is None:
        # Format #2: permission string was provided directly
        required_permission = module_or_permission
    else:
        # Format #1: module and action were provided separately
        required_permission = f"{module_or_permission}:{action}"
    
    # Check for exact permission match using both formats
    # Check for standard format (e.g., "inventory_items:read")
    if required_permission in user_permissions:
        return True
        
    # Check for module:action format (e.g., "inventory_items:read")
    if required_permission in user_permissions:
        return True
        
    # Check for legacy format with underscore (e.g., "inventory_items_read")
    legacy_format = required_permission.replace(":", "_")
    if legacy_format in user_permissions:
        return True
    
    # Check for "all" permission (admin wildcard)
    if "all" in user_permissions:
        return True
        
    return False
    """
    
    # Replace the function in the content
    new_content = content.replace(old_function, new_function)
    
    # Write the updated content back to the file
    with open(permissions_file, "w") as f:
        f.write(new_content)
    
    print("✅ Permission checker function updated successfully!")

# Create a script to update roles with proper permissions
def update_role_permissions():
    """Update role permissions to match the expected format"""
    
    db = SessionLocal()
    try:
        # Get all roles
        roles = db.query(Role).all()
        
        # Update the Administrator role to ensure it has "all" permission
        admin_role = next((r for r in roles if r.name == "Administrator"), None)
        if admin_role:
            # Ensure admin has the "all" permission
            if "all" not in admin_role.permissions:
                admin_role.permissions.append("all")
                print(f"Added 'all' permission to Administrator role")
                
        # Update the Accountant role
        accountant_role = next((r for r in roles if r.name == "Accountant"), None)
        if accountant_role:
            # Fix the inventory:item:read permission (should be inventory_items:read)
            if "inventory:item:read" in accountant_role.permissions:
                accountant_role.permissions.remove("inventory:item:read")
                accountant_role.permissions.append("inventory_items:read")
                print(f"Updated inventory permission for Accountant role")
                
            # Ensure Accountant has AP/AR transaction permissions in both formats
            accountant_permissions = [
                "ap:transaction:read",
                "ap:transaction:create",
                "ap:transaction:view", 
                "ar:transaction:read",
                "ar:transaction:view",
                "inventory_items:read"
            ]
            
            for perm in accountant_permissions:
                if perm not in accountant_role.permissions:
                    accountant_role.permissions.append(perm)
                    print(f"Added {perm} to Accountant role")
                    
        # Update the Sales role
        sales_role = next((r for r in roles if r.name == "Sales"), None)
        if sales_role:
            # Ensure Sales has inventory_items:read
            if "inventory_items:read" not in sales_role.permissions:
                sales_role.permissions.append("inventory_items:read")
                print(f"Added inventory_items:read to Sales role")
        
        # Commit changes to the database
        db.commit()
        print("✅ Role permissions updated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating role permissions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Fix the permission checker
    fix_permission_checker()
    
    # Update role permissions
    update_role_permissions()
