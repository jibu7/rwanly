#!/usr/bin/env python3
"""
Update RBAC role permissions to fix the failing test scenarios.
This script updates the permissions for existing roles in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.models.core import Role
from app.core.permissions import DEFAULT_ROLES

def update_role_permissions():
    """Update role permissions in the database"""
    db = SessionLocal()
    try:
        print("🔄 Updating role permissions...")
        
        # Get all roles from database
        roles = db.query(Role).all()
        
        updated_count = 0
        for role in roles:
            if role.name in DEFAULT_ROLES:
                old_permissions = role.permissions or []
                new_permissions = DEFAULT_ROLES[role.name]
                
                if set(old_permissions) != set(new_permissions):
                    print(f"Updating role '{role.name}':")
                    print(f"  Old permissions count: {len(old_permissions)}")
                    print(f"  New permissions count: {len(new_permissions)}")
                    
                    # Update the role permissions
                    role.permissions = new_permissions
                    updated_count += 1
                else:
                    print(f"Role '{role.name}' permissions are already up to date")
        
        if updated_count > 0:
            db.commit()
            print(f"✅ Successfully updated {updated_count} roles")
        else:
            print("✅ All roles are already up to date")
            
        # Print summary of current permissions
        print("\n📊 Current role permissions summary:")
        for role in roles:
            if role.name in DEFAULT_ROLES:
                permissions = role.permissions or []
                print(f"  {role.name}: {len(permissions)} permissions")
                
                # Check specific permissions for debugging
                if role.name == "Accountant":
                    has_ar_view = "ar:transaction:view" in permissions
                    has_ap_view = "ap:transaction:view" in permissions
                    has_user_read = "sys:user:read" in permissions
                    has_company_read = "sys:company:read" in permissions
                    print(f"    - AR transactions view: {has_ar_view}")
                    print(f"    - AP transactions view: {has_ap_view}")
                    print(f"    - User read (should be False): {has_user_read}")
                    print(f"    - Company read (should be False): {has_company_read}")
                elif role.name == "Sales":
                    has_user_read = "sys:user:read" in permissions
                    print(f"    - User read (should be False): {has_user_read}")
                    
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating role permissions: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_role_permissions()
