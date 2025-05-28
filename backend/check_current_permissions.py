#!/usr/bin/env python3
"""
Script to check current role permissions in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.database.database import SessionLocal
from app.models.core import Role, UserRole, User
from sqlalchemy import create_engine

def check_role_permissions():
    """Check current role permissions in database"""
    
    db = SessionLocal()
    try:
        # Get all roles with their permissions
        roles = db.query(Role).all()
        
        print("=" * 60)
        print("CURRENT ROLE PERMISSIONS IN DATABASE")
        print("=" * 60)
        
        for role in roles:
            print(f"\n🔑 ROLE: {role.name}")
            print(f"   Description: {role.description}")
            
            # Permissions are stored as JSONB in the role
            permissions = role.permissions or []
            
            if permissions:
                print(f"   Permissions ({len(permissions)}):")
                for perm in permissions:
                    print(f"     - {perm}")
            else:
                print("   Permissions: NONE")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        for role in roles:
            perm_count = len(role.permissions or [])
            print(f"{role.name}: {perm_count} permissions")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_role_permissions()
