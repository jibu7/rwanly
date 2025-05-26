from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date
from app.models import User, Company, Role, UserRole, AccountingPeriod
from app.schemas import UserCreate, UserUpdate, CompanyCreate, CompanyUpdate, RoleCreate, RoleUpdate, AccountingPeriodCreate, AccountingPeriodUpdate
from app.core.security import get_password_hash


class UserCRUD:
    """CRUD operations for User model"""
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_company(self, db: Session, company_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).filter(User.company_id == company_id).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            company_id=user_data.company_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=user_data.is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete(self, db: Session, user_id: int) -> bool:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    def assign_role(self, db: Session, user_id: int, role_id: int) -> bool:
        # Check if assignment already exists
        existing = db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        ).first()
        
        if existing:
            return False
        
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        db.commit()
        return True
    
    def remove_role(self, db: Session, user_id: int, role_id: int) -> bool:
        user_role = db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        ).first()
        
        if not user_role:
            return False
        
        db.delete(user_role)
        db.commit()
        return True


class CompanyCRUD:
    """CRUD operations for Company model"""
    
    def get_by_id(self, db: Session, company_id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.id == company_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()
    
    def create(self, db: Session, company_data: CompanyCreate) -> Company:
        db_company = Company(**company_data.dict())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    
    def update(self, db: Session, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
        db_company = self.get_by_id(db, company_id)
        if not db_company:
            return None
        
        update_data = company_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)
        
        db.commit()
        db.refresh(db_company)
        return db_company


class RoleCRUD:
    """CRUD operations for Role model"""
    
    def get_by_id(self, db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()
    
    def get_by_company(self, db: Session, company_id: int, skip: int = 0, limit: int = 100) -> List[Role]:
        return db.query(Role).filter(Role.company_id == company_id).offset(skip).limit(limit).all()
    
    def create(self, db: Session, role_data: RoleCreate) -> Role:
        db_role = Role(**role_data.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def update(self, db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        db_role = self.get_by_id(db, role_id)
        if not db_role:
            return None
        
        update_data = role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def delete(self, db: Session, role_id: int) -> bool:
        db_role = self.get_by_id(db, role_id)
        if not db_role:
            return False
        
        db.delete(db_role)
        db.commit()
        return True


class AccountingPeriodCRUD:
    """CRUD operations for AccountingPeriod model"""
    
    def get_by_id(self, db: Session, period_id: int) -> Optional[AccountingPeriod]:
        return db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id).first()
    
    def get_by_company(self, db: Session, company_id: int, skip: int = 0, limit: int = 100) -> List[AccountingPeriod]:
        return db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == company_id
        ).order_by(AccountingPeriod.financial_year.desc(), AccountingPeriod.start_date).offset(skip).limit(limit).all()
    
    def get_by_financial_year(self, db: Session, company_id: int, financial_year: int) -> List[AccountingPeriod]:
        return db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.company_id == company_id,
                AccountingPeriod.financial_year == financial_year
            )
        ).order_by(AccountingPeriod.start_date).all()
    
    def get_current_period(self, db: Session, company_id: int, transaction_date: date = None) -> Optional[AccountingPeriod]:
        """Get the accounting period for a given date (defaults to today)"""
        if transaction_date is None:
            transaction_date = date.today()
        
        return db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.company_id == company_id,
                AccountingPeriod.start_date <= transaction_date,
                AccountingPeriod.end_date >= transaction_date
            )
        ).first()
    
    def get_open_periods(self, db: Session, company_id: int) -> List[AccountingPeriod]:
        """Get all open (not closed) accounting periods"""
        return db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.company_id == company_id,
                AccountingPeriod.is_closed == False
            )
        ).order_by(AccountingPeriod.start_date).all()
    
    def check_period_overlap(self, db: Session, company_id: int, start_date: date, end_date: date, exclude_id: int = None) -> bool:
        """Check if a new period would overlap with existing periods"""
        query = db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.company_id == company_id,
                or_(
                    and_(AccountingPeriod.start_date <= start_date, AccountingPeriod.end_date >= start_date),
                    and_(AccountingPeriod.start_date <= end_date, AccountingPeriod.end_date >= end_date),
                    and_(AccountingPeriod.start_date >= start_date, AccountingPeriod.end_date <= end_date)
                )
            )
        )
        
        if exclude_id:
            query = query.filter(AccountingPeriod.id != exclude_id)
        
        return query.first() is not None
    
    def create(self, db: Session, period_data: AccountingPeriodCreate) -> AccountingPeriod:
        """Create a new accounting period with validation"""
        # Check for overlapping periods
        if self.check_period_overlap(db, period_data.company_id, period_data.start_date, period_data.end_date):
            raise ValueError("Accounting period overlaps with existing period")
        
        # Validate dates
        if period_data.start_date >= period_data.end_date:
            raise ValueError("Start date must be before end date")
        
        db_period = AccountingPeriod(**period_data.dict())
        db.add(db_period)
        db.commit()
        db.refresh(db_period)
        return db_period
    
    def update(self, db: Session, period_id: int, period_data: AccountingPeriodUpdate) -> Optional[AccountingPeriod]:
        db_period = self.get_by_id(db, period_id)
        if not db_period:
            return None
        
        update_data = period_data.dict(exclude_unset=True)
        
        # Validate date changes
        start_date = update_data.get('start_date', db_period.start_date)
        end_date = update_data.get('end_date', db_period.end_date)
        
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        # Check for overlapping periods if dates are being changed
        if 'start_date' in update_data or 'end_date' in update_data:
            if self.check_period_overlap(db, db_period.company_id, start_date, end_date, exclude_id=period_id):
                raise ValueError("Accounting period overlaps with existing period")
        
        for field, value in update_data.items():
            setattr(db_period, field, value)
        
        db.commit()
        db.refresh(db_period)
        return db_period
    
    def close_period(self, db: Session, period_id: int) -> Optional[AccountingPeriod]:
        """Close an accounting period"""
        db_period = self.get_by_id(db, period_id)
        if not db_period:
            return None
        
        db_period.is_closed = True
        db.commit()
        db.refresh(db_period)
        return db_period
    
    def reopen_period(self, db: Session, period_id: int) -> Optional[AccountingPeriod]:
        """Reopen a closed accounting period"""
        db_period = self.get_by_id(db, period_id)
        if not db_period:
            return None
        
        db_period.is_closed = False
        db.commit()
        db.refresh(db_period)
        return db_period
    
    def delete(self, db: Session, period_id: int) -> bool:
        """Delete an accounting period (only if no transactions exist)"""
        db_period = self.get_by_id(db, period_id)
        if not db_period:
            return False
        
        # TODO: Check for existing transactions in this period before deletion
        # This will be implemented when transaction models are created
        
        db.delete(db_period)
        db.commit()
        return True


# Create instances
user_crud = UserCRUD()
company_crud = CompanyCRUD()
role_crud = RoleCRUD()
accounting_period_crud = AccountingPeriodCRUD()
