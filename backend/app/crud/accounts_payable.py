from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.models.core import (
    Supplier, APTransactionType, APTransaction, APAllocation
)
from app.schemas.core import (
    SupplierCreate, SupplierUpdate,
    APTransactionTypeCreate, APTransactionTypeUpdate,
    APTransactionCreate, APTransactionUpdate,
    APAllocationCreate
)


class SupplierCRUD:
    def update_supplier_balance(self, db: Session, supplier_id: int, company_id: int, amount: Decimal, increase: bool = True) -> bool:
        supplier = self.get_supplier(db, supplier_id, company_id)
        if not supplier:
            return False
        if increase:
            supplier.current_balance = (supplier.current_balance or Decimal('0.00')) + amount
        else:
            supplier.current_balance = (supplier.current_balance or Decimal('0.00')) - amount
        db.commit()
        db.refresh(supplier)
        return True
    """CRUD operations for Supplier model - REQ-AP-SUPP-*"""
    def get_supplier(self, db: Session, supplier_id: int, company_id: int) -> Optional[Supplier]:
        return db.query(Supplier).filter(and_(Supplier.id == supplier_id, Supplier.company_id == company_id)).first()

    def get_suppliers(self, db: Session, company_id: int, is_active: Optional[bool] = None) -> List[Supplier]:
        query = db.query(Supplier).filter(Supplier.company_id == company_id)
        if is_active is not None:
            query = query.filter(Supplier.is_active == is_active)
        return query.order_by(Supplier.supplier_code).all()

    def create_supplier(self, db: Session, supplier: SupplierCreate) -> Supplier:
        db_supplier = Supplier(**supplier.model_dump())
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier

    def update_supplier(self, db: Session, supplier_id: int, company_id: int, supplier_update: SupplierUpdate) -> Optional[Supplier]:
        db_supplier = self.get_supplier(db, supplier_id, company_id)
        if not db_supplier:
            return None
        update_data = supplier_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_supplier, field, value)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier

    def delete_supplier(self, db: Session, supplier_id: int, company_id: int) -> bool:
        db_supplier = self.get_supplier(db, supplier_id, company_id)
        if not db_supplier:
            return False
        db.delete(db_supplier)
        db.commit()
        return True


class APTransactionTypeCRUD:
    """CRUD operations for AP Transaction Type model - REQ-AP-TT-*"""
    def get_transaction_type(self, db: Session, type_id: int, company_id: int) -> Optional[APTransactionType]:
        return db.query(APTransactionType).filter(and_(APTransactionType.id == type_id, APTransactionType.company_id == company_id)).first()

    def get_transaction_type_by_code(self, db: Session, type_code: str, company_id: int) -> Optional[APTransactionType]:
        return db.query(APTransactionType).filter(and_(APTransactionType.type_code == type_code, APTransactionType.company_id == company_id)).first()

    def get_transaction_types(self, db: Session, company_id: int, is_active: Optional[bool] = None) -> List[APTransactionType]:
        query = db.query(APTransactionType).filter(APTransactionType.company_id == company_id)
        if is_active is not None:
            query = query.filter(APTransactionType.is_active == is_active)
        return query.order_by(APTransactionType.type_code).all()

    def create_transaction_type(self, db: Session, transaction_type: APTransactionTypeCreate) -> APTransactionType:
        db_type = APTransactionType(**transaction_type.model_dump())
        db.add(db_type)
        db.commit()
        db.refresh(db_type)
        return db_type

    def update_transaction_type(self, db: Session, type_id: int, company_id: int, type_update: APTransactionTypeUpdate) -> Optional[APTransactionType]:
        db_type = self.get_transaction_type(db, type_id, company_id)
        if not db_type:
            return None
        update_data = type_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_type, field, value)
        db.commit()
        db.refresh(db_type)
        return db_type


class APTransactionCRUD:
    """CRUD operations for AP Transaction model - REQ-AP-TP-*"""
    def get_transaction(self, db: Session, transaction_id: int, company_id: int) -> Optional[APTransaction]:
        return db.query(APTransaction).filter(and_(APTransaction.id == transaction_id, APTransaction.company_id == company_id)).first()

    def get_transactions(self, db: Session, company_id: int, supplier_id: Optional[int] = None, transaction_type_id: Optional[int] = None, date_from: Optional[date] = None, date_to: Optional[date] = None, is_posted: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[APTransaction]:
        query = db.query(APTransaction).filter(APTransaction.company_id == company_id)
        if supplier_id:
            query = query.filter(APTransaction.supplier_id == supplier_id)
        if transaction_type_id:
            query = query.filter(APTransaction.transaction_type_id == transaction_type_id)
        if date_from:
            query = query.filter(APTransaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(APTransaction.transaction_date <= date_to)
        if is_posted is not None:
            query = query.filter(APTransaction.is_posted == is_posted)
        return query.order_by(desc(APTransaction.transaction_date), desc(APTransaction.created_at)).offset(skip).limit(limit).all()

    def create_transaction(self, db: Session, transaction: APTransactionCreate) -> APTransaction:
        net_amount = Decimal(str(transaction.gross_amount)) + Decimal(str(transaction.tax_amount or 0)) - Decimal(str(transaction.discount_amount or 0))
        db_transaction = APTransaction(
            **transaction.model_dump(),
            net_amount=net_amount,
            outstanding_amount=net_amount
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def update_transaction(self, db: Session, transaction_id: int, company_id: int, transaction_update: APTransactionUpdate) -> Optional[APTransaction]:
        db_transaction = self.get_transaction(db, transaction_id, company_id)
        if not db_transaction:
            return None
        if db_transaction.is_posted:
            raise ValueError("Cannot update posted transaction")
        update_data = transaction_update.model_dump(exclude_unset=True)
        if any(field in update_data for field in ['gross_amount', 'tax_amount', 'discount_amount']):
            from decimal import Decimal
            def to_decimal(val):
                if isinstance(val, Decimal):
                    return val
                try:
                    return Decimal(str(val))
                except Exception:
                    return Decimal('0.00')
            gross = to_decimal(update_data.get('gross_amount', db_transaction.gross_amount))
            tax = to_decimal(update_data.get('tax_amount', db_transaction.tax_amount))
            discount = to_decimal(update_data.get('discount_amount', db_transaction.discount_amount))
            net_amount = gross + tax - discount
            update_data['net_amount'] = net_amount
            update_data['outstanding_amount'] = net_amount
        for field, value in update_data.items():
            setattr(db_transaction, field, value)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def post_transaction(self, db: Session, transaction_id: int, company_id: int, posted_by: int) -> Optional[APTransaction]:
        db_transaction = self.get_transaction(db, transaction_id, company_id)
        if not db_transaction:
            return None
        if db_transaction.is_posted:
            raise ValueError("Transaction already posted")
        db_transaction.is_posted = True
        db_transaction.posted_by = posted_by
        db_transaction.posted_at = datetime.utcnow()
        # Update supplier balance
        supplier_crud.update_supplier_balance(
            db, db_transaction.supplier_id, company_id,
            Decimal(str(db_transaction.net_amount)),
            increase=(db_transaction.transaction_type.affects_balance == "CREDIT")
        )
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def get_outstanding_invoices(self, db: Session, company_id: int, supplier_id: Optional[int] = None) -> List[APTransaction]:
        from app.models.core import APTransactionType
        query = db.query(APTransaction).filter(
            and_(
                APTransaction.company_id == company_id,
                APTransaction.is_posted == True,
                APTransaction.outstanding_amount > 0
            )
        )
        if supplier_id:
            query = query.filter(APTransaction.supplier_id == supplier_id)
        query = query.join(APTransactionType).filter(APTransactionType.affects_balance == "DEBIT")
        return query.order_by(APTransaction.transaction_date).all()


class APAllocationCRUD:
    """CRUD operations for AP Allocation model - REQ-AP-ALLOC-*"""
    def create_allocation(self, db: Session, allocation: APAllocationCreate, posted_by: int) -> APAllocation:
        db_allocation = APAllocation(**allocation.model_dump(), posted_by=posted_by)
        db.add(db_allocation)
        db.commit()
        db.refresh(db_allocation)
        return db_allocation

    def get_allocations(self, db: Session, company_id: int, supplier_id: Optional[int] = None) -> List[APAllocation]:
        query = db.query(APAllocation).filter(APAllocation.company_id == company_id)
        if supplier_id:
            query = query.filter(APAllocation.supplier_id == supplier_id)
        return query.order_by(desc(APAllocation.allocation_date)).all()


# Create instances
supplier_crud = SupplierCRUD()
ap_transaction_type_crud = APTransactionTypeCRUD()
ap_transaction_crud = APTransactionCRUD()
ap_allocation_crud = APAllocationCRUD()
