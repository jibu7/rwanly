from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date

from app.models.core import (
    InventoryItem, InventoryTransactionType, InventoryTransaction,
    GLTransaction, AccountingPeriod
)
from app.schemas.core import (
    InventoryItemCreate, InventoryItemUpdate,
    InventoryTransactionTypeCreate, InventoryTransactionTypeUpdate,
    InventoryTransactionCreate, InventoryTransactionUpdate
)


class InventoryItemCRUD:
    """CRUD operations for Inventory Items"""
    
    @staticmethod
    def create(db: Session, *, obj_in: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item"""
        # Map frontend field names to backend field names
        gl_asset_account_id = obj_in.gl_account_inventory_id
        gl_expense_account_id = obj_in.gl_account_cogs_id  
        gl_revenue_account_id = obj_in.gl_account_sales_id
        
        db_obj = InventoryItem(
            company_id=obj_in.company_id,
            item_code=obj_in.item_code,
            description=obj_in.description,
            item_type=obj_in.item_type,
            unit_of_measure=obj_in.unit_of_measure,
            cost_price=obj_in.cost_price,
            selling_price=obj_in.selling_price,
            costing_method=obj_in.costing_method,
            reorder_level=obj_in.reorder_level,
            reorder_quantity=obj_in.reorder_quantity,
            gl_asset_account_id=gl_asset_account_id,
            gl_expense_account_id=gl_expense_account_id,
            gl_revenue_account_id=gl_revenue_account_id,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, id: int) -> Optional[InventoryItem]:
        """Get an inventory item by ID"""
        return db.query(InventoryItem).filter(InventoryItem.id == id).first()
    
    @staticmethod
    def get_by_code(db: Session, company_id: int, item_code: str) -> Optional[InventoryItem]:
        """Get an inventory item by code"""
        return db.query(InventoryItem).filter(
            InventoryItem.company_id == company_id,
            InventoryItem.item_code == item_code
        ).first()
    
    @staticmethod
    def get_multi(
        db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[InventoryItem]:
        """Get multiple inventory items"""
        return db.query(InventoryItem).filter(
            InventoryItem.company_id == company_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session, *, db_obj: InventoryItem, obj_in: InventoryItemUpdate
    ) -> InventoryItem:
        """Update an inventory item"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Map frontend field names to backend field names
        if 'gl_account_inventory_id' in update_data:
            update_data['gl_asset_account_id'] = update_data.pop('gl_account_inventory_id')
        if 'gl_account_cogs_id' in update_data:
            update_data['gl_expense_account_id'] = update_data.pop('gl_account_cogs_id')
        if 'gl_account_sales_id' in update_data:
            update_data['gl_revenue_account_id'] = update_data.pop('gl_account_sales_id')
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class InventoryTransactionTypeCRUD:
    """CRUD operations for Inventory Transaction Types"""
    
    @staticmethod
    def create(db: Session, *, obj_in: InventoryTransactionTypeCreate) -> InventoryTransactionType:
        """Create a new transaction type"""
        db_obj = InventoryTransactionType(
            company_id=obj_in.company_id,
            type_code=obj_in.type_code,
            type_name=obj_in.type_name,
            description=obj_in.description,
            affects_quantity=obj_in.affects_quantity,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, id: int) -> Optional[InventoryTransactionType]:
        """Get a transaction type by ID"""
        return db.query(InventoryTransactionType).filter(InventoryTransactionType.id == id).first()
    
    @staticmethod
    def get_by_code(
        db: Session, company_id: int, type_code: str
    ) -> Optional[InventoryTransactionType]:
        """Get a transaction type by code"""
        return db.query(InventoryTransactionType).filter(
            InventoryTransactionType.company_id == company_id,
            InventoryTransactionType.type_code == type_code
        ).first()
    
    @staticmethod
    def get_multi(
        db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[InventoryTransactionType]:
        """Get multiple transaction types"""
        return db.query(InventoryTransactionType).filter(
            InventoryTransactionType.company_id == company_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session, *, db_obj: InventoryTransactionType, obj_in: InventoryTransactionTypeUpdate
    ) -> InventoryTransactionType:
        """Update a transaction type"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class InventoryTransactionCRUD:
    """CRUD operations for Inventory Transactions"""
    
    @staticmethod
    def _create_gl_entries(
        db: Session,
        company_id: int,
        accounting_period_id: int,
        transaction: InventoryTransaction,
        item: InventoryItem,
        transaction_type: InventoryTransactionType,
        posted_by: int
    ) -> None:
        """Create GL entries for inventory transactions."""
        # Determine if this is a stock receipt or issue
        is_receipt = transaction_type.affects_quantity == "INCREASE"
        
        # Create GL entries based on transaction type
        gl_entries = []
        
        if transaction.source_module == "INV":
            # For inventory adjustments
            gl_entries = [
                GLTransaction(
                    company_id=company_id,
                    accounting_period_id=accounting_period_id,
                    gl_account_id=item.gl_asset_account_id,
                    transaction_date=transaction.transaction_date,
                    reference_number=transaction.reference_number,
                    description=transaction.description,
                    debit_amount=transaction.total_cost if is_receipt else 0,
                    credit_amount=0 if is_receipt else transaction.total_cost,
                    source_module="INV",
                    source_document_id=transaction.id,
                    posted_by=posted_by,
                    is_posted=True
                ),
                GLTransaction(
                    company_id=company_id,
                    accounting_period_id=accounting_period_id,
                    gl_account_id=item.gl_expense_account_id,
                    transaction_date=transaction.transaction_date,
                    reference_number=transaction.reference_number,
                    description=transaction.description,
                    debit_amount=0 if is_receipt else transaction.total_cost,
                    credit_amount=transaction.total_cost if is_receipt else 0,
                    source_module="INV",
                    source_document_id=transaction.id,
                    posted_by=posted_by,
                    is_posted=True
                )
            ]
        elif transaction.source_module == "AP":
            # For purchases, we don't create GL entries here
            # They will be created by the AP module
            pass
        elif transaction.source_module == "AR":
            # For sales, we don't create GL entries here
            # They will be created by the AR module
            pass
        
        # Add GL entries to the session
        for entry in gl_entries:
            db.add(entry)

    # Update the create method to include GL entry creation
    @staticmethod
    def create(
        db: Session, *, obj_in: InventoryTransactionCreate, posted_by: int
    ) -> InventoryTransaction:
        """Create a new inventory transaction"""
        # Calculate total cost
        total_cost = abs(obj_in.quantity * obj_in.unit_cost)
        
        # Create transaction
        db_obj = InventoryTransaction(
            company_id=obj_in.company_id,
            item_id=obj_in.item_id,
            transaction_type_id=obj_in.transaction_type_id,
            accounting_period_id=obj_in.accounting_period_id,
            transaction_date=obj_in.transaction_date,
            reference_number=obj_in.reference_number,
            description=obj_in.description,
            quantity=obj_in.quantity,
            unit_cost=obj_in.unit_cost,
            total_cost=total_cost,
            source_module=obj_in.source_module,
            source_document_id=obj_in.source_document_id,
            posted_by=posted_by,
            posted_at=func.now(),
            is_posted=True
        )
        db.add(db_obj)
        
        # Update item quantity and cost
        item = db.query(InventoryItem).filter(InventoryItem.id == obj_in.item_id).first()
        if not item:
            raise ValueError("Invalid item_id")
            
        transaction_type = db.query(InventoryTransactionType).filter(
            InventoryTransactionType.id == obj_in.transaction_type_id
        ).first()
        if not transaction_type:
            raise ValueError("Invalid transaction_type_id")
        
        # Update quantity based on transaction type
        quantity_change = obj_in.quantity
        if transaction_type.affects_quantity == "DECREASE":
            quantity_change = -obj_in.quantity
        
        new_quantity = item.quantity_on_hand + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient stock quantity")
            
        # Update weighted average cost if it's a stock receipt
        if transaction_type.affects_quantity == "INCREASE" and quantity_change > 0:
            new_total_value = (
                item.quantity_on_hand * item.cost_price + 
                quantity_change * obj_in.unit_cost
            )
            item.cost_price = new_total_value / new_quantity if new_quantity > 0 else obj_in.unit_cost
            
        item.quantity_on_hand = new_quantity
        db.add(item)
        
        # Create GL entries if the transaction is posted
        if db_obj.is_posted:
            InventoryTransactionCRUD._create_gl_entries(
                db=db,
                company_id=obj_in.company_id,
                accounting_period_id=obj_in.accounting_period_id,
                transaction=db_obj,
                item=item,
                transaction_type=transaction_type,
                posted_by=posted_by
            )
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, id: int) -> Optional[InventoryTransaction]:
        """Get a transaction by ID"""
        return db.query(InventoryTransaction).filter(InventoryTransaction.id == id).first()
    
    @staticmethod
    def get_multi(
        db: Session, *, 
        company_id: int, 
        item_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[InventoryTransaction]:
        """Get multiple transactions"""
        query = db.query(InventoryTransaction).filter(
            InventoryTransaction.company_id == company_id
        )
        if item_id:
            query = query.filter(InventoryTransaction.item_id == item_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_stock_level_report(
        db: Session, *, company_id: int, as_at_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get stock level report"""
        query = db.query(
            InventoryItem.id,
            InventoryItem.item_code,
            InventoryItem.description,
            InventoryItem.unit_of_measure,
            InventoryItem.quantity_on_hand,
            InventoryItem.cost_price,
            (InventoryItem.quantity_on_hand * InventoryItem.cost_price).label('total_value')
        ).filter(
            InventoryItem.company_id == company_id,
            InventoryItem.item_type == 'STOCK',
            InventoryItem.is_active == True
        )
        
        if as_at_date:
            # TODO: Calculate historical stock levels
            pass
            
        return [dict(row) for row in query.all()]
    
    @staticmethod
    def get_transaction_history(
        db: Session, *, company_id: int, item_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get transaction history for an item"""
        query = db.query(InventoryTransaction).filter(
            InventoryTransaction.company_id == company_id,
            InventoryTransaction.item_id == item_id
        )
        
        if from_date:
            query = query.filter(InventoryTransaction.transaction_date >= from_date)
        if to_date:
            query = query.filter(InventoryTransaction.transaction_date <= to_date)
            
        transactions = query.order_by(InventoryTransaction.transaction_date).all()
        
        # Calculate running totals
        running_quantity = 0
        running_value = 0
        result = []
        
        for transaction in transactions:
            type_affects_quantity = transaction.transaction_type.affects_quantity
            quantity_change = (
                transaction.quantity if type_affects_quantity == "INCREASE"
                else -transaction.quantity
            )
            
            running_quantity += quantity_change
            value_change = quantity_change * transaction.unit_cost
            running_value += value_change
            
            result.append({
                "transaction_id": transaction.id,
                "transaction_date": transaction.transaction_date,
                "reference_number": transaction.reference_number,
                "transaction_type": transaction.transaction_type.type_name,
                "description": transaction.description,
                "quantity": quantity_change,
                "unit_cost": transaction.unit_cost,
                "total_cost": transaction.total_cost,
                "running_quantity": running_quantity,
                "running_value": running_value
            })
            
        return result
