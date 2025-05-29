from typing import List


# Define all available permissions in the system
class Permissions:
    """Define all system permissions based on PRD requirements"""
    
    # System Core Permissions
    SYS_USER_CREATE = "sys:user:create"
    SYS_USER_READ = "sys:user:read"
    SYS_USER_UPDATE = "sys:user:update"
    SYS_USER_DELETE = "sys:user:delete"
    
    SYS_ROLE_CREATE = "sys:role:create"
    SYS_ROLE_READ = "sys:role:read"
    SYS_ROLE_UPDATE = "sys:role:update"
    SYS_ROLE_DELETE = "sys:role:delete"
    
    SYS_COMPANY_CREATE = "sys:company:create"
    SYS_COMPANY_READ = "sys:company:read"
    SYS_COMPANY_UPDATE = "sys:company:update"
    SYS_COMPANY_DELETE = "sys:company:delete"
    
    SYS_ACCOUNTING_PERIOD_CREATE = "sys:accounting_period:create"
    SYS_ACCOUNTING_PERIOD_READ = "sys:accounting_period:read"
    SYS_ACCOUNTING_PERIOD_UPDATE = "sys:accounting_period:update"
    SYS_ACCOUNTING_PERIOD_DELETE = "sys:accounting_period:delete"
    SYS_ACCOUNTING_PERIOD_CLOSE = "sys:accounting_period:close"
    SYS_ACCOUNTING_PERIOD_REOPEN = "sys:accounting_period:reopen"
    
    # General Ledger Permissions (Future)
    GL_ACCOUNT_CREATE = "gl:account:create"
    GL_ACCOUNT_READ = "gl:account:read"
    GL_ACCOUNT_UPDATE = "gl:account:update"
    GL_JOURNAL_CREATE = "gl:journal:create"
    GL_JOURNAL_POST = "gl:journal:post"
    GL_REPORT_VIEW = "gl:report:view"
    
    # Accounts Receivable Permissions (REQ-AR-*)
    # Customer Management
    AR_CREATE_CUSTOMERS = "ar:customer:create"
    AR_VIEW_CUSTOMERS = "ar:customer:view"
    AR_EDIT_CUSTOMERS = "ar:customer:edit"
    AR_DELETE_CUSTOMERS = "ar:customer:delete"
    
    # Transaction Types
    AR_CREATE_TRANSACTION_TYPES = "ar:transaction_type:create"
    AR_VIEW_TRANSACTION_TYPES = "ar:transaction_type:view"
    AR_EDIT_TRANSACTION_TYPES = "ar:transaction_type:edit"
    AR_DELETE_TRANSACTION_TYPES = "ar:transaction_type:delete"
    
    # Transactions
    AR_CREATE_TRANSACTIONS = "ar:transaction:create"
    AR_VIEW_TRANSACTIONS = "ar:transaction:view"
    AR_EDIT_TRANSACTIONS = "ar:transaction:edit"
    AR_POST_TRANSACTIONS = "ar:transaction:post"
    
    # Allocations
    AR_CREATE_ALLOCATIONS = "ar:allocation:create"
    AR_VIEW_ALLOCATIONS = "ar:allocation:view"
    
    # Ageing
    AR_VIEW_AGEING = "ar:ageing:view"
    AR_SETUP_AGEING = "ar:ageing:setup"
    AR_MANAGE_AGEING_PERIODS = "ar:ageing:manage"
    
    # Reports
    AR_VIEW_REPORTS = "ar:report:view"
    
    # Accounts Payable Permissions (REQ-AP-*)
    # Supplier Management
    AP_CREATE_SUPPLIERS = "ap:supplier:create"
    AP_VIEW_SUPPLIERS = "ap:supplier:view" 
    AP_EDIT_SUPPLIERS = "ap:supplier:edit"
    AP_DELETE_SUPPLIERS = "ap:supplier:delete"
    
    # Transaction Types
    AP_CREATE_TRANSACTION_TYPES = "ap:transaction_type:create"
    AP_VIEW_TRANSACTION_TYPES = "ap:transaction_type:view"
    AP_EDIT_TRANSACTION_TYPES = "ap:transaction_type:edit"
    AP_DELETE_TRANSACTION_TYPES = "ap:transaction_type:delete"
    
    # Transactions
    AP_CREATE_TRANSACTIONS = "ap:transaction:create"
    AP_VIEW_TRANSACTIONS = "ap:transaction:view"
    AP_EDIT_TRANSACTIONS = "ap:transaction:edit"
    AP_POST_TRANSACTIONS = "ap:transaction:post"
    
    # Allocations
    AP_ALLOCATE_PAYMENTS = "ap:allocation:create"
    AP_VIEW_ALLOCATIONS = "ap:allocation:view"
    
    # Ageing
    AP_VIEW_AGEING = "ap:ageing:view"
    AP_SETUP_AGEING = "ap:ageing:setup"
    
    # Reports
    AP_VIEW_REPORTS = "ap:report:view"
    
    # Legacy permissions (keeping for compatibility)
    AP_SUPPLIER_CREATE = "ap:supplier:create"
    AP_SUPPLIER_READ = "ap:supplier:read"
    AP_SUPPLIER_UPDATE = "ap:supplier:update"
    AP_TRANSACTION_CREATE = "ap:transaction:create"
    AP_TRANSACTION_POST = "ap:transaction:post"
    AP_REPORT_VIEW = "ap:report:view"
    
    # Inventory Permissions (REQ-INV-*)
    INV_ITEM_CREATE = "inventory_items:create"
    INV_ITEM_READ = "inventory_items:read"
    INV_ITEM_UPDATE = "inventory_items:update"
    INV_ITEM_DELETE = "inventory_items:delete"
    
    INV_TRANSACTION_TYPE_CREATE = "inventory_transaction_types:create"
    INV_TRANSACTION_TYPE_READ = "inventory_transaction_types:read"
    INV_TRANSACTION_TYPE_UPDATE = "inventory_transaction_types:update"
    INV_TRANSACTION_TYPE_DELETE = "inventory_transaction_types:delete"
    
    INV_TRANSACTION_CREATE = "inventory_transactions:create"
    INV_TRANSACTION_READ = "inventory_transactions:read"
    INV_TRANSACTION_UPDATE = "inventory_transactions:update"
    INV_TRANSACTION_POST = "inventory_transactions:post"
    
    INV_ADJUSTMENT_CREATE = "inventory_adjustments:create"
    INV_ADJUSTMENT_READ = "inventory_adjustments:read"
    INV_ADJUSTMENT_UPDATE = "inventory_adjustments:update"
    INV_ADJUSTMENT_DELETE = "inventory_adjustments:delete"
    
    INV_REPORT_VIEW = "inventory_reports:read"

    # Order Entry Permissions (Future)
    OE_SALES_ORDER_CREATE = "oe:sales_order:create"
    OE_SALES_ORDER_READ = "oe:sales_order:read"
    OE_SALES_ORDER_UPDATE = "oe:sales_order:update"
    OE_PURCHASE_ORDER_CREATE = "oe:purchase_order:create"
    OE_PURCHASE_ORDER_READ = "oe:purchase_order:read"
    OE_PURCHASE_ORDER_UPDATE = "oe:purchase_order:update"
    OE_REPORT_VIEW = "oe:report:view"


def get_all_permissions() -> List[str]:
    """Get all available permissions in the system"""
    return [
        getattr(Permissions, attr) for attr in dir(Permissions)
        if not attr.startswith('_') and isinstance(getattr(Permissions, attr), str)
    ]


def check_permission(user_or_permissions, module_or_permission, action=None):
    """
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
    """
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
    
    return False


# Default role permissions
DEFAULT_ROLES = {
    "Administrator": get_all_permissions(),
    "Accountant": [
        # Remove SYS_USER_READ and SYS_COMPANY_READ - accountants should not manage users/companies
        Permissions.SYS_ACCOUNTING_PERIOD_READ,
        Permissions.SYS_ACCOUNTING_PERIOD_CREATE,
        Permissions.SYS_ACCOUNTING_PERIOD_UPDATE,
        Permissions.SYS_ACCOUNTING_PERIOD_CLOSE,
        Permissions.SYS_ACCOUNTING_PERIOD_REOPEN,
        # General Ledger permissions
        Permissions.GL_ACCOUNT_CREATE,
        Permissions.GL_ACCOUNT_READ,
        Permissions.GL_ACCOUNT_UPDATE,
        Permissions.GL_JOURNAL_CREATE,
        Permissions.GL_JOURNAL_POST,
        Permissions.GL_REPORT_VIEW,
        # Accounts Receivable permissions
        Permissions.AR_VIEW_CUSTOMERS,
        Permissions.AR_VIEW_TRANSACTIONS,  # Add missing permission
        Permissions.AR_CREATE_TRANSACTIONS,
        Permissions.AR_POST_TRANSACTIONS,
        Permissions.AR_VIEW_REPORTS,
        # Accounts Payable permissions
        Permissions.AP_SUPPLIER_READ,
        Permissions.AP_VIEW_TRANSACTIONS,  # Add missing permission
        Permissions.AP_TRANSACTION_CREATE,
        Permissions.AP_TRANSACTION_POST,
        Permissions.AP_REPORT_VIEW,
    ],
    "Sales": [
        # Remove SYS_USER_READ - sales should not access user management
        Permissions.AR_CREATE_CUSTOMERS,
        Permissions.AR_VIEW_CUSTOMERS,
        Permissions.AR_EDIT_CUSTOMERS,
        Permissions.INV_ITEM_READ,
        Permissions.OE_SALES_ORDER_CREATE,
        Permissions.OE_SALES_ORDER_READ,
        Permissions.OE_SALES_ORDER_UPDATE,
        Permissions.OE_REPORT_VIEW,
    ],
    "Purchasing": [
        Permissions.SYS_USER_READ,
        Permissions.AP_SUPPLIER_CREATE,
        Permissions.AP_SUPPLIER_READ,
        Permissions.AP_SUPPLIER_UPDATE,
        Permissions.INV_ITEM_READ,
        Permissions.OE_PURCHASE_ORDER_CREATE,
        Permissions.OE_PURCHASE_ORDER_READ,
        Permissions.OE_PURCHASE_ORDER_UPDATE,
        Permissions.OE_REPORT_VIEW,
    ],
    "Warehouse": [
        Permissions.SYS_USER_READ,
        Permissions.INV_ITEM_READ,
        Permissions.INV_ADJUSTMENT_CREATE,
        Permissions.INV_REPORT_VIEW,
        Permissions.OE_SALES_ORDER_READ,
        Permissions.OE_PURCHASE_ORDER_READ,
    ],
    "Clerk": [
        Permissions.SYS_USER_READ,
        Permissions.AR_VIEW_CUSTOMERS,
        Permissions.AP_SUPPLIER_READ,
        Permissions.INV_ITEM_READ,
        Permissions.OE_SALES_ORDER_READ,
        Permissions.OE_PURCHASE_ORDER_READ,
    ]
}
