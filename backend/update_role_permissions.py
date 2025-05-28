#!/usr/bin/env python3
"""
Update role permissions to match the DEFAULT_ROLES configuration
"""

from sqlalchemy.orm import sessionmaker
from app.database.database import engine
from app.models.core import Role
from app.core.permissions import DEFAULT_ROLES

def update_role_permissions():
    """Update role permissions in database to match DEFAULT_ROLES"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔄 Updating role permissions...")
        
        for role_name, expected_permissions in DEFAULT_ROLES.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                print(f"\n📝 Updating {role_name} role:")
                print(f"   Current permissions: {len(role.permissions)}")
                print(f"   Expected permissions: {len(expected_permissions)}")
                
                # Update permissions
                role.permissions = expected_permissions
                print(f"   ✓ Updated to {len(role.permissions)} permissions")
                
                # Show some key permissions for verification
                key_perms = [p for p in expected_permissions if any(x in p for x in ['gl:', 'ar:', 'ap:', 'sys:'])][:5]
                print(f"   Sample permissions: {key_perms}")
            else:
                print(f"❌ Role {role_name} not found")
        
        db.commit()
        print("\n✅ Role permissions updated successfully!")
        
        # Verify the changes
        print("\n🔍 Verification:")
        for role_name in DEFAULT_ROLES.keys():
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                print(f"   {role_name}: {len(role.permissions)} permissions")
        
    except Exception as e:
        print(f"❌ Error updating permissions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_role_permissions()
