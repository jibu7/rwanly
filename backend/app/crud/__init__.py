# Import CRUD instances for easy access
from .core import user_crud, company_crud, role_crud, accounting_period_crud

__all__ = ["user_crud", "company_crud", "role_crud", "accounting_period_crud"]
