#!/usr/bin/env python3
"""
Test script to verify inventory permissions mapping
"""

def test_permission_mapping():
    """Test the permission mapping logic from auth.py"""
    
    # Simulate the permission mapping logic
    permission_strings = [
        "inventory_items:read",
        "inventory_items:create", 
        "inventory_items:update",
        "inventory_items:delete",
        "inventory_transactions:read",
        "inventory_reports:read"
    ]
    
    permissions = []
    
    for perm_str in permission_strings:
        frontend_resource = None
        action = None
        
        # Handle permissions with underscore format like "inventory_items:read"
        if '_' in perm_str and ':' in perm_str:
            parts = perm_str.split(':')
            if len(parts) >= 2:
                resource_part = parts[0]
                action = parts[1]
                
                if resource_part.startswith('inventory'):
                    frontend_resource = 'inventory'
        
        if frontend_resource and action:
            permissions.append({
                "resource": frontend_resource,
                "action": action
            })
    
    print("Permission mapping test:")
    print(f"Input permissions: {permission_strings}")
    print(f"Mapped permissions: {permissions}")
    
    # Check if we have inventory read permission
    has_inventory_read = any(
        p['resource'] == 'inventory' and p['action'] == 'read' 
        for p in permissions
    )
    
    print(f"Has inventory read permission: {has_inventory_read}")
    
    return permissions

if __name__ == "__main__":
    test_permission_mapping()
