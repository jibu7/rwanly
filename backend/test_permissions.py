#!/usr/bin/env python3
"""
Test script to check permission mapping
"""
from sqlalchemy.orm import sessionmaker
from app.database.database import engine
from app.models.core import Role

def test_permissions():
    """Test the permission mapping between backend and frontend"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Get the admin role
        admin_role = db.query(Role).filter(Role.name == 'Administrator').first()
        if not admin_role:
            print("Administrator role not found!")
            return
        
        # Count all permissions and inventory permissions
        permissions = admin_role.permissions
        print(f"Total permissions: {len(permissions)}")
        
        # Count inventory permissions
        inventory_perms = [p for p in permissions if 'inventory' in p]
        print(f"Inventory permissions: {len(inventory_perms)}")
        print("Inventory permissions found:")
        for p in inventory_perms:
            print(f"  - {p}")
            
        # Check if inventory read permission exists
        has_inventory_read = any(
            p.startswith('inventory') and ':read' in p 
            for p in permissions
        )
        print(f"Has inventory:read permission: {has_inventory_read}")
        
        # Check other read permissions for comparison
        read_perms = [p for p in permissions if ':read' in p]
        print("Read permissions found:")
        for p in read_perms[:5]:  # Show just the first 5
            print(f"  - {p}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_permissions()
