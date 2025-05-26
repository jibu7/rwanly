from fastapi import APIRouter
from app.api import auth, users, companies, roles, accounting_periods, general_ledger, accounts_receivable, accounts_payable, inventory, order_entry

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(accounting_periods.router, tags=["Accounting Periods"])
api_router.include_router(general_ledger.router, prefix="/gl", tags=["General Ledger"])
api_router.include_router(accounts_receivable.router, prefix="/ar", tags=["Accounts Receivable"])
api_router.include_router(accounts_payable.router, prefix="/ap", tags=["Accounts Payable"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(order_entry.router, prefix="/oe", tags=["Order Entry"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "rwanly Core ERP API is running"}
