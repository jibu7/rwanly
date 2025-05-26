from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case, desc, asc, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.models.core import (
    Customer, ARTransactionType, ARTransaction, ARAllocation, AgeingPeriod
)
from app.schemas.core import (
    CustomerCreate, CustomerUpdate, 
    ARTransactionTypeCreate, ARTransactionTypeUpdate,
    ARTransactionCreate, ARTransactionUpdate,
    ARAllocationCreate,
    AgeingPeriodCreate, AgeingPeriodUpdate,
    CustomerAgeingItem, CustomerAgeingReport,
    CustomerTransactionItem, CustomerTransactionReport
)


class CustomerCRUD:
    """CRUD operations for Customer model - REQ-AR-CUST-*"""
    
    def get_customer(self, db: Session, customer_id: int, company_id: int) -> Optional[Customer]:
        """Get a single customer by ID for a specific company"""
        return db.query(Customer).filter(
            and_(Customer.id == customer_id, Customer.company_id == company_id)
        ).first()
    
    def get_customer_by_code(self, db: Session, customer_code: str, company_id: int) -> Optional[Customer]:
        """Get a customer by customer code for a specific company"""
        return db.query(Customer).filter(
            and_(Customer.customer_code == customer_code, Customer.company_id == company_id)
        ).first()
    
    def get_customers(self, db: Session, company_id: int, skip: int = 0, limit: int = 100, 
                     is_active: Optional[bool] = None, search: Optional[str] = None) -> List[Customer]:
        """Get customers for a company with optional filtering"""
        query = db.query(Customer).filter(Customer.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.customer_code.ilike(search_term),
                    Customer.name.ilike(search_term)
                )
            )
            
        return query.order_by(Customer.customer_code).offset(skip).limit(limit).all()
    
    def create_customer(self, db: Session, customer: CustomerCreate) -> Customer:
        """Create a new customer"""
        db_customer = Customer(**customer.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    def update_customer(self, db: Session, customer_id: int, company_id: int, 
                       customer_update: CustomerUpdate) -> Optional[Customer]:
        """Update an existing customer"""
        db_customer = self.get_customer(db, customer_id, company_id)
        if not db_customer:
            return None
        
        update_data = customer_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    def delete_customer(self, db: Session, customer_id: int, company_id: int) -> bool:
        """Soft delete a customer (mark as inactive)"""
        db_customer = self.get_customer(db, customer_id, company_id)
        if not db_customer:
            return False
        
        db_customer.is_active = False
        db.commit()
        return True
    
    def update_customer_balance(self, db: Session, customer_id: int, company_id: int, 
                               amount: Decimal, increase: bool = True) -> Optional[Customer]:
        """Update customer balance"""
        db_customer = self.get_customer(db, customer_id, company_id)
        if not db_customer:
            return None
        
        if increase:
            db_customer.current_balance += amount
        else:
            db_customer.current_balance -= amount
        
        db.commit()
        db.refresh(db_customer)
        return db_customer


class ARTransactionTypeCRUD:
    """CRUD operations for AR Transaction Type model - REQ-AR-TT-*"""
    
    def get_transaction_type(self, db: Session, type_id: int, company_id: int) -> Optional[ARTransactionType]:
        """Get a single AR transaction type by ID"""
        return db.query(ARTransactionType).filter(
            and_(ARTransactionType.id == type_id, ARTransactionType.company_id == company_id)
        ).first()
    
    def get_transaction_type_by_code(self, db: Session, type_code: str, company_id: int) -> Optional[ARTransactionType]:
        """Get AR transaction type by code"""
        return db.query(ARTransactionType).filter(
            and_(ARTransactionType.type_code == type_code, ARTransactionType.company_id == company_id)
        ).first()
    
    def get_transaction_types(self, db: Session, company_id: int, 
                             is_active: Optional[bool] = None) -> List[ARTransactionType]:
        """Get AR transaction types for a company"""
        query = db.query(ARTransactionType).filter(ARTransactionType.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(ARTransactionType.is_active == is_active)
            
        return query.order_by(ARTransactionType.type_code).all()
    
    def create_transaction_type(self, db: Session, transaction_type: ARTransactionTypeCreate) -> ARTransactionType:
        """Create a new AR transaction type"""
        db_type = ARTransactionType(**transaction_type.model_dump())
        db.add(db_type)
        db.commit()
        db.refresh(db_type)
        return db_type
    
    def update_transaction_type(self, db: Session, type_id: int, company_id: int,
                               type_update: ARTransactionTypeUpdate) -> Optional[ARTransactionType]:
        """Update an existing AR transaction type"""
        db_type = self.get_transaction_type(db, type_id, company_id)
        if not db_type:
            return None
        
        update_data = type_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_type, field, value)
        
        db.commit()
        db.refresh(db_type)
        return db_type


class ARTransactionCRUD:
    """CRUD operations for AR Transaction model - REQ-AR-TP-*"""
    
    def get_transaction(self, db: Session, transaction_id: int, company_id: int) -> Optional[ARTransaction]:
        """Get a single AR transaction by ID"""
        return db.query(ARTransaction).filter(
            and_(ARTransaction.id == transaction_id, ARTransaction.company_id == company_id)
        ).first()
    
    def get_transactions(self, db: Session, company_id: int, 
                        customer_id: Optional[int] = None,
                        transaction_type_id: Optional[int] = None,
                        date_from: Optional[date] = None,
                        date_to: Optional[date] = None,
                        is_posted: Optional[bool] = None,
                        skip: int = 0, limit: int = 100) -> List[ARTransaction]:
        """Get AR transactions with filtering"""
        query = db.query(ARTransaction).filter(ARTransaction.company_id == company_id)
        
        if customer_id:
            query = query.filter(ARTransaction.customer_id == customer_id)
        if transaction_type_id:
            query = query.filter(ARTransaction.transaction_type_id == transaction_type_id)
        if date_from:
            query = query.filter(ARTransaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(ARTransaction.transaction_date <= date_to)
        if is_posted is not None:
            query = query.filter(ARTransaction.is_posted == is_posted)
            
        return query.order_by(desc(ARTransaction.transaction_date), 
                             desc(ARTransaction.created_at)).offset(skip).limit(limit).all()
    
    def create_transaction(self, db: Session, transaction: ARTransactionCreate) -> ARTransaction:
        """Create a new AR transaction"""
        # Calculate net amount
        net_amount = transaction.gross_amount + (transaction.tax_amount or 0) - (transaction.discount_amount or 0)
        
        db_transaction = ARTransaction(
            **transaction.model_dump(),
            net_amount=net_amount,
            outstanding_amount=net_amount  # Initially all outstanding
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    
    def update_transaction(self, db: Session, transaction_id: int, company_id: int,
                          transaction_update: ARTransactionUpdate) -> Optional[ARTransaction]:
        """Update an existing AR transaction"""
        db_transaction = self.get_transaction(db, transaction_id, company_id)
        if not db_transaction:
            return None
        
        if db_transaction.is_posted:
            raise ValueError("Cannot update posted transaction")
        
        update_data = transaction_update.model_dump(exclude_unset=True)
        
        # Recalculate net amount if financial fields changed
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
            update_data['outstanding_amount'] = net_amount  # Reset outstanding amount
        
        for field, value in update_data.items():
            setattr(db_transaction, field, value)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    
    def post_transaction(self, db: Session, transaction_id: int, company_id: int, 
                        posted_by: int) -> Optional[ARTransaction]:
        """Post an AR transaction to GL"""
        db_transaction = self.get_transaction(db, transaction_id, company_id)
        if not db_transaction:
            return None
        
        if db_transaction.is_posted:
            raise ValueError("Transaction already posted")
        
        # Mark as posted
        db_transaction.is_posted = True
        db_transaction.posted_by = posted_by
        db_transaction.posted_at = datetime.utcnow()
        
        # Update customer balance
        customer_crud.update_customer_balance(
            db, db_transaction.customer_id, company_id, 
            Decimal(str(db_transaction.net_amount)), 
            increase=(db_transaction.transaction_type.affects_balance == "DEBIT")
        )
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    
    def get_outstanding_invoices(self, db: Session, company_id: int, 
                                customer_id: Optional[int] = None) -> List[ARTransaction]:
        """Get outstanding invoices for allocation"""
        query = db.query(ARTransaction).filter(
            and_(
                ARTransaction.company_id == company_id,
                ARTransaction.is_posted == True,
                ARTransaction.outstanding_amount > 0
            )
        )
        
        if customer_id:
            query = query.filter(ARTransaction.customer_id == customer_id)
        
        # Typically we want invoices for allocation
        query = query.join(ARTransactionType).filter(
            ARTransactionType.affects_balance == "DEBIT"
        )
        
        return query.order_by(ARTransaction.transaction_date).all()


class ARAllocationCRUD:
    """CRUD operations for AR Allocation model - REQ-AR-ALLOC-*"""
    
    def create_allocation(self, db: Session, allocation: ARAllocationCreate, 
                         posted_by: int) -> ARAllocation:
        """Create a new AR allocation"""
        db_allocation = ARAllocation(
            **allocation.model_dump(),
            posted_by=posted_by
        )
        
        # Update outstanding amounts
        payment = db.query(ARTransaction).filter(ARTransaction.id == allocation.transaction_id).first()
        invoice = db.query(ARTransaction).filter(ARTransaction.id == allocation.allocated_to_id).first()
        
        if not payment or not invoice:
            raise ValueError("Invalid transaction IDs for allocation")
        
        # Update outstanding amounts
        payment.outstanding_amount -= Decimal(str(allocation.allocated_amount))
        invoice.outstanding_amount -= Decimal(str(allocation.allocated_amount))
        
        db.add(db_allocation)
        db.commit()
        db.refresh(db_allocation)
        return db_allocation
    
    def get_allocations(self, db: Session, company_id: int, 
                       customer_id: Optional[int] = None,
                       transaction_id: Optional[int] = None) -> List[ARAllocation]:
        """Get AR allocations"""
        query = db.query(ARAllocation).filter(ARAllocation.company_id == company_id)
        
        if customer_id:
            query = query.filter(ARAllocation.customer_id == customer_id)
        if transaction_id:
            query = query.filter(
                or_(
                    ARAllocation.transaction_id == transaction_id,
                    ARAllocation.allocated_to_id == transaction_id
                )
            )
        
        return query.order_by(desc(ARAllocation.allocation_date)).all()


class AgeingPeriodCRUD:
    """CRUD operations for Ageing Period model - REQ-AR-AGE-*"""
    
    def get_ageing_periods(self, db: Session, company_id: int) -> List[AgeingPeriod]:
        """Get ageing periods for a company"""
        return db.query(AgeingPeriod).filter(
            and_(AgeingPeriod.company_id == company_id, AgeingPeriod.is_active == True)
        ).order_by(AgeingPeriod.sort_order).all()
    
    def create_ageing_period(self, db: Session, period: AgeingPeriodCreate) -> AgeingPeriod:
        """Create a new ageing period"""
        db_period = AgeingPeriod(**period.model_dump())
        db.add(db_period)
        db.commit()
        db.refresh(db_period)
        return db_period
    
    def setup_default_ageing_periods(self, db: Session, company_id: int) -> List[AgeingPeriod]:
        """Setup default ageing periods for a company"""
        default_periods = [
            {"period_name": "Current", "days_from": 0, "days_to": 29, "sort_order": 1},
            {"period_name": "30 Days", "days_from": 30, "days_to": 59, "sort_order": 2},
            {"period_name": "60 Days", "days_from": 60, "days_to": 89, "sort_order": 3},
            {"period_name": "90 Days", "days_from": 90, "days_to": 119, "sort_order": 4},
            {"period_name": "Over 120", "days_from": 120, "days_to": 999999, "sort_order": 5},
        ]
        
        created_periods = []
        for period_data in default_periods:
            period = AgeingPeriodCreate(company_id=company_id, **period_data)
            created_periods.append(self.create_ageing_period(db, period))
        
        return created_periods


class ARReportingCRUD:
    """CRUD operations for AR Reporting - REQ-AR-REPORT-*"""
    
    def generate_customer_ageing_report(self, db: Session, company_id: int, 
                                       as_at_date: Optional[date] = None) -> CustomerAgeingReport:
        """Generate customer ageing report"""
        if not as_at_date:
            as_at_date = date.today()
        
        # Get ageing periods
        ageing_periods = db.query(AgeingPeriod).filter(
            and_(AgeingPeriod.company_id == company_id, AgeingPeriod.is_active == True)
        ).order_by(AgeingPeriod.sort_order).all()
        
        # Get customers with outstanding balances
        customers = db.query(Customer).filter(
            and_(
                Customer.company_id == company_id,
                Customer.current_balance != 0,
                Customer.is_active == True
            )
        ).all()
        
        report_items = []
        summary = {"current": 0, "period_30": 0, "period_60": 0, "period_90": 0, "over_90": 0, "total": 0}
        
        for customer in customers:
            # Get outstanding transactions for this customer
            outstanding_transactions = db.query(ARTransaction).filter(
                and_(
                    ARTransaction.company_id == company_id,
                    ARTransaction.customer_id == customer.id,
                    ARTransaction.is_posted == True,
                    ARTransaction.outstanding_amount > 0,
                    ARTransaction.transaction_date <= as_at_date
                )
            ).all()
            
            # Calculate aging buckets
            aging_buckets = {"current": 0, "period_30": 0, "period_60": 0, "period_90": 0, "over_90": 0}
            
            for transaction in outstanding_transactions:
                days_outstanding = (as_at_date - transaction.transaction_date).days
                amount = float(transaction.outstanding_amount)
                
                # Determine which bucket this falls into
                if days_outstanding <= 29:
                    aging_buckets["current"] += amount
                elif days_outstanding <= 59:
                    aging_buckets["period_30"] += amount
                elif days_outstanding <= 89:
                    aging_buckets["period_60"] += amount
                elif days_outstanding <= 119:
                    aging_buckets["period_90"] += amount
                else:
                    aging_buckets["over_90"] += amount
            
            total_outstanding = sum(aging_buckets.values())
            
            if total_outstanding > 0:
                item = CustomerAgeingItem(
                    customer_id=customer.id,
                    customer_code=customer.customer_code,
                    customer_name=customer.name,
                    current_balance=float(customer.current_balance),
                    **aging_buckets,
                    total_outstanding=total_outstanding
                )
                report_items.append(item)
                
                # Update summary
                for key in aging_buckets:
                    summary[key] += aging_buckets[key]
                summary["total"] += total_outstanding
        
        return CustomerAgeingReport(
            as_at_date=as_at_date,
            customers=report_items,
            summary=summary
        )
    
    def generate_customer_transaction_report(self, db: Session, company_id: int, 
                                           customer_id: int,
                                           date_from: Optional[date] = None,
                                           date_to: Optional[date] = None) -> CustomerTransactionReport:
        """Generate customer transaction report"""
        customer = db.query(Customer).filter(
            and_(Customer.id == customer_id, Customer.company_id == company_id)
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Get transactions
        query = db.query(ARTransaction).filter(
            and_(
                ARTransaction.company_id == company_id,
                ARTransaction.customer_id == customer_id,
                ARTransaction.is_posted == True
            )
        )
        
        if date_from:
            query = query.filter(ARTransaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(ARTransaction.transaction_date <= date_to)
        
        transactions = query.order_by(ARTransaction.transaction_date).all()
        
        report_items = []
        total_gross = 0
        total_outstanding = 0
        
        for transaction in transactions:
            days_outstanding = None
            if transaction.outstanding_amount > 0:
                days_outstanding = (date.today() - transaction.transaction_date).days
            
            item = CustomerTransactionItem(
                transaction_id=transaction.id,
                transaction_date=transaction.transaction_date,
                reference_number=transaction.reference_number,
                transaction_type=transaction.transaction_type.type_name,
                description=transaction.description,
                gross_amount=float(transaction.gross_amount),
                outstanding_amount=float(transaction.outstanding_amount),
                days_outstanding=days_outstanding
            )
            report_items.append(item)
            
            total_gross += float(transaction.gross_amount)
            total_outstanding += float(transaction.outstanding_amount)
        
        summary = {
            "total_gross": total_gross,
            "total_outstanding": total_outstanding,
            "transaction_count": len(transactions)
        }
        
        return CustomerTransactionReport(
            customer=customer,
            transactions=report_items,
            summary=summary
        )


# Create instances
customer_crud = CustomerCRUD()
ar_transaction_type_crud = ARTransactionTypeCRUD()
ar_transaction_crud = ARTransactionCRUD()
ar_allocation_crud = ARAllocationCRUD()
ageing_period_crud = AgeingPeriodCRUD()
ar_reporting_crud = ARReportingCRUD()
