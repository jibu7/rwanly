#!/usr/bin/env python3
"""
Final permission fixes for RBAC system.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.database.database import engine, SessionLocal
from app.models.core import Role, User, UserRole
from app.core.permissions import Permissions

def fix_accounts_receivable_api():
    """
    Fix the accounts_receivable.py API file.
    """
    ar_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "app", "api", "accounts_receivable.py")
    
    # Get the content first to see what we're working with
    with open(ar_file, "r") as f:
        content = f.read()
    
    # Look for the transactions GET endpoint
    if "@router.get(\"/transactions\"" in content:
        # Find the line with require_permission and modify it
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "@router.get(\"/transactions\"" in line:
                # Look ahead for the require_permission line
                for j in range(i, min(i+15, len(lines))):
                    if "require_permission" in lines[j]:
                        # Replace the permission check
                        if "AR_VIEW_TRANSACTIONS" in lines[j]:
                            print("AR transactions endpoint already using correct permission")
                        else:
                            old_line = lines[j]
                            lines[j] = lines[j].replace("require_permission(", 
                                                     "require_permission(Permissions.AR_VIEW_TRANSACTIONS")
                            print(f"Fixed AR transactions endpoint: {old_line} -> {lines[j]}")
                        break
        
        # Write the updated content
        with open(ar_file, "w") as f:
            f.write("\n".join(lines))
        
        print("✅ Updated accounts_receivable.py endpoint")
    else:
        print("⚠️ Could not find AR transactions endpoint")

def fix_accounts_payable_api():
    """
    Fix the accounts_payable.py API file.
    """
    ap_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "app", "api", "accounts_payable.py")
    
    # Get the content first to see what we're working with
    with open(ap_file, "r") as f:
        content = f.read()
    
    # Look for the transactions GET endpoint
    if "@router.get(\"/transactions\"" in content:
        # Find the line with require_permission and modify it
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "@router.get(\"/transactions\"" in line:
                # Look ahead for the require_permission line
                for j in range(i, min(i+15, len(lines))):
                    if "require_permission" in lines[j]:
                        # Replace the permission check
                        if "AP_VIEW_TRANSACTIONS" in lines[j]:
                            print("AP transactions endpoint already using correct permission")
                        else:
                            old_line = lines[j]
                            lines[j] = lines[j].replace("require_permission(", 
                                                     "require_permission(Permissions.AP_VIEW_TRANSACTIONS")
                            print(f"Fixed AP transactions endpoint: {old_line} -> {lines[j]}")
                        break
        
        # Write the updated content
        with open(ap_file, "w") as f:
            f.write("\n".join(lines))
        
        print("✅ Updated accounts_payable.py endpoint")
    else:
        print("⚠️ Could not find AP transactions endpoint")

def update_role_permissions_final():
    """Update role permissions with final fixes"""
    
    db = SessionLocal()
    try:
        # Get all roles
        roles = db.query(Role).all()
        
        # Update the Accountant role
        accountant_role = next((r for r in roles if r.name == "Accountant"), None)
        if accountant_role:
            # Make sure the accountant role has SYS_COMPANY_READ permission
            if Permissions.SYS_COMPANY_READ not in accountant_role.permissions:
                accountant_role.permissions.append(Permissions.SYS_COMPANY_READ)
                print(f"Added {Permissions.SYS_COMPANY_READ} to Accountant role")
                
            # Make sure the accountant role has AR_VIEW_TRANSACTIONS in the exact format
            if Permissions.AR_VIEW_TRANSACTIONS not in accountant_role.permissions:
                accountant_role.permissions.append(Permissions.AR_VIEW_TRANSACTIONS)
                print(f"Added {Permissions.AR_VIEW_TRANSACTIONS} to Accountant role")
                
            # Make sure the accountant role has AP_VIEW_TRANSACTIONS in the exact format
            if Permissions.AP_VIEW_TRANSACTIONS not in accountant_role.permissions:
                accountant_role.permissions.append(Permissions.AP_VIEW_TRANSACTIONS)
                print(f"Added {Permissions.AP_VIEW_TRANSACTIONS} to Accountant role")
        
        # Commit changes to the database
        db.commit()
        print("✅ Role permissions updated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating role permissions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Fix API endpoints
    fix_accounts_receivable_api()
    fix_accounts_payable_api()
    
    # Final role permission updates
    update_role_permissions_final()
