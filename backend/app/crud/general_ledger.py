from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from typing import List, Optional
from datetime import date
from app.models.core import GLAccount, GLTransaction, AccountingPeriod
from app.schemas.core import (
    GLAccountCreate, GLAccountUpdate,
    GLTransactionCreate, GLTransactionUpdate,
    TrialBalanceItem
)


class GLAccountCRUD:
    """CRUD operations for General Ledger Accounts"""
    
    def get_account(self, db: Session, account_id: int, company_id: int) -> Optional[GLAccount]:
        """Get a single GL account by ID for a specific company"""
        return db.query(GLAccount).filter(
            and_(GLAccount.id == account_id, GLAccount.company_id == company_id)
        ).first()
    
    def get_account_by_code(self, db: Session, account_code: str, company_id: int) -> Optional[GLAccount]:
        """Get a GL account by account code for a specific company"""
        return db.query(GLAccount).filter(
            and_(GLAccount.account_code == account_code, GLAccount.company_id == company_id)
        ).first()
    
    def get_accounts(self, db: Session, company_id: int, skip: int = 0, limit: int = 100, 
                    account_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[GLAccount]:
        """Get GL accounts for a company with optional filtering"""
        query = db.query(GLAccount).filter(GLAccount.company_id == company_id)
        
        if account_type:
            query = query.filter(GLAccount.account_type == account_type)
        if is_active is not None:
            query = query.filter(GLAccount.is_active == is_active)
            
        return query.order_by(GLAccount.account_code).offset(skip).limit(limit).all()
    
    def create_account(self, db: Session, account: GLAccountCreate) -> GLAccount:
        """Create a new GL account"""
        db_account = GLAccount(**account.model_dump())
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    
    def update_account(self, db: Session, account_id: int, company_id: int, 
                      account_update: GLAccountUpdate) -> Optional[GLAccount]:
        """Update an existing GL account"""
        db_account = self.get_account(db, account_id, company_id)
        if not db_account:
            return None
            
        update_data = account_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_account, field, value)
            
        db.commit()
        db.refresh(db_account)
        return db_account
    
    def delete_account(self, db: Session, account_id: int, company_id: int) -> bool:
        """Soft delete a GL account (set is_active to False)"""
        db_account = self.get_account(db, account_id, company_id)
        if not db_account:
            return False
            
        # Check if account has transactions
        has_transactions = db.query(GLTransaction).filter(
            GLTransaction.gl_account_id == account_id
        ).first() is not None
        
        if has_transactions:
            # Soft delete - can't hard delete accounts with transactions
            db_account.is_active = False
        else:
            # Hard delete if no transactions
            db.delete(db_account)
            
        db.commit()
        return True


class GLTransactionCRUD:
    """CRUD operations for General Ledger Transactions"""
    
    def get_transaction(self, db: Session, transaction_id: int, company_id: int) -> Optional[GLTransaction]:
        """Get a single GL transaction by ID for a specific company"""
        return db.query(GLTransaction).filter(
            and_(GLTransaction.id == transaction_id, GLTransaction.company_id == company_id)
        ).first()
    
    def get_transactions(self, db: Session, company_id: int, skip: int = 0, limit: int = 100,
                        account_id: Optional[int] = None, period_id: Optional[int] = None,
                        start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[GLTransaction]:
        """Get GL transactions for a company with optional filtering"""
        query = db.query(GLTransaction).filter(GLTransaction.company_id == company_id)
        
        if account_id:
            query = query.filter(GLTransaction.gl_account_id == account_id)
        if period_id:
            query = query.filter(GLTransaction.accounting_period_id == period_id)
        if start_date:
            query = query.filter(GLTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(GLTransaction.transaction_date <= end_date)
            
        return query.order_by(GLTransaction.transaction_date.desc(), GLTransaction.id.desc()).offset(skip).limit(limit).all()
    
    def create_transaction(self, db: Session, transaction: GLTransactionCreate) -> GLTransaction:
        """Create a new GL transaction"""
        # Validate that either debit or credit is non-zero, but not both
        if (transaction.debit_amount > 0 and transaction.credit_amount > 0) or \
           (transaction.debit_amount == 0 and transaction.credit_amount == 0):
            raise ValueError("Transaction must have either a debit amount or credit amount, but not both")
            
        db_transaction = GLTransaction(**transaction.model_dump())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    
    def update_transaction(self, db: Session, transaction_id: int, company_id: int,
                          transaction_update: GLTransactionUpdate) -> Optional[GLTransaction]:
        """Update an existing GL transaction"""
        db_transaction = self.get_transaction(db, transaction_id, company_id)
        if not db_transaction:
            return None
            
        # Check if the accounting period is closed
        period = db.query(AccountingPeriod).filter(
            AccountingPeriod.id == db_transaction.accounting_period_id
        ).first()
        if period and period.is_closed:
            raise ValueError("Cannot modify transactions in a closed accounting period")
            
        update_data = transaction_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_transaction, field, value)
            
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    
    def delete_transaction(self, db: Session, transaction_id: int, company_id: int) -> bool:
        """Delete a GL transaction"""
        db_transaction = self.get_transaction(db, transaction_id, company_id)
        if not db_transaction:
            return False
            
        # Check if the accounting period is closed
        period = db.query(AccountingPeriod).filter(
            AccountingPeriod.id == db_transaction.accounting_period_id
        ).first()
        if period and period.is_closed:
            raise ValueError("Cannot delete transactions in a closed accounting period")
            
        db.delete(db_transaction)
        db.commit()
        return True
    
    def get_trial_balance(self, db: Session, company_id: int, period_id: int) -> List[TrialBalanceItem]:
        """Generate trial balance for a specific accounting period"""
        # Get the accounting period
        period = db.query(AccountingPeriod).filter(
            and_(AccountingPeriod.id == period_id, AccountingPeriod.company_id == company_id)
        ).first()
        
        if not period:
            raise ValueError("Accounting period not found")
        
        # Query to calculate account balances
        balance_query = db.query(
            GLAccount.id.label('account_id'),
            GLAccount.account_code,
            GLAccount.account_name,
            GLAccount.account_type,
            func.sum(GLTransaction.debit_amount).label('total_debits'),
            func.sum(GLTransaction.credit_amount).label('total_credits')
        ).join(
            GLTransaction, GLAccount.id == GLTransaction.gl_account_id
        ).filter(
            and_(
                GLAccount.company_id == company_id,
                GLTransaction.accounting_period_id == period_id,
                GLAccount.is_active == True
            )
        ).group_by(
            GLAccount.id, GLAccount.account_code, GLAccount.account_name, GLAccount.account_type
        ).order_by(GLAccount.account_code).all()
        
        trial_balance_items = []
        for row in balance_query:
            debit_balance = 0.0
            credit_balance = 0.0
            
            # Calculate net balance based on account type and normal balance
            net_balance = float(row.total_debits or 0) - float(row.total_credits or 0)
            
            # Determine if balance should show as debit or credit
            account = db.query(GLAccount).filter(GLAccount.id == row.account_id).first()
            if account:
                if account.normal_balance == "DEBIT":
                    if net_balance >= 0:
                        debit_balance = net_balance
                    else:
                        credit_balance = abs(net_balance)
                else:  # CREDIT normal balance
                    if net_balance <= 0:
                        credit_balance = abs(net_balance)
                    else:
                        debit_balance = net_balance
            
            trial_balance_items.append(TrialBalanceItem(
                account_id=row.account_id,
                account_code=row.account_code,
                account_name=row.account_name,
                account_type=row.account_type,
                debit_balance=debit_balance,
                credit_balance=credit_balance
            ))
        
        return trial_balance_items


# Create instances
gl_account_crud = GLAccountCRUD()
gl_transaction_crud = GLTransactionCRUD()
