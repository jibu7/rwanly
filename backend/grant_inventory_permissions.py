#!/usr/bin/env python3
"""
Grant inventory permissions to admin user
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.database.database import engine, SessionLocal
from app.models.core import Role, User, UserRole
from app.core.permissions import Permissions, get_all_permissions

def grant_inventory_permissions():
    """Grant inventory permissions to admin user"""
    db = SessionLocal()
    
    try:
        print("🔄 Granting inventory permissions to admin...")
        
        # Find admin user
        admin_user = db.query(User).filter(User.email == "admin@techflow.com").first()
        if not admin_user:
            print("❌ Admin user not found")
            return
            
        print(f"✓ Found admin user: {admin_user.email}")
        
        # Find Administrator role
        admin_role = db.query(Role).filter(Role.name == "Administrator").first()
        if not admin_role:
            print("❌ Administrator role not found")
            return
            
        print(f"✓ Found Administrator role")
        
        # Get all permissions including inventory
        all_permissions = get_all_permissions()
        inventory_permissions = [p for p in all_permissions if 'inventory' in p.lower() or 'inv:' in p]
        
        print(f"📦 Found {len(inventory_permissions)} inventory permissions:")
        for perm in inventory_permissions:
            print(f"   - {perm}")
        
        # Update admin role with all permissions
        admin_role.permissions = all_permissions
        
        print(f"\n✅ Updated Administrator role with {len(all_permissions)} total permissions")
        
        # Ensure admin user has Administrator role
        user_role = db.query(UserRole).filter(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id
        ).first()
        
        if not user_role:
            user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.add(user_role)
            print("✓ Assigned Administrator role to admin user")
        else:
            print("✓ Admin user already has Administrator role")
        
        db.commit()
        print("\n🎉 Successfully granted inventory permissions to admin!")
        print("\nPlease refresh your browser to see the inventory module in the dashboard.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    grant_inventory_permissions()
