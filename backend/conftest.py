"""
Pytest configuration and fixtures for backend tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.models.core import User, Role, UserRole, Company, Customer, Supplier
from app.core.security import get_password_hash


# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with proper configuration for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

# Create test session maker
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    """Set up test database for the session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(setup_database):
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_company(db: Session):
    """Create a test company"""
    company = Company(
        name="Test Company Ltd",
        registration_number="TEST123",
        tax_number="TAX456",
        address="123 Test Street, Test City",
        contact_email="test@company.com",
        contact_phone="123-456-7890",
        is_active=True
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture 
def test_user(db: Session, test_company: Company):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass"),
        company_id=test_company.id,
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_customer(db: Session, test_company: Company):
    """Create a test customer"""
    customer = Customer(
        code="CUST001", 
        name="Test Customer Ltd",
        company_id=test_company.id,
        contact_person="John Doe",
        email="customer@test.com",
        phone="123-456-7890",
        address="123 Customer Street",
        credit_limit=10000.00,
        is_active=True
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def test_supplier(db: Session, test_company: Company):
    """Create a test supplier"""
    supplier = Supplier(
        code="SUPP001",
        name="Test Supplier Inc", 
        company_id=test_company.id,
        contact_person="Jane Smith",
        email="supplier@test.com",
        phone="098-765-4321",
        address="456 Supplier Avenue",
        credit_limit=50000.00,
        is_active=True
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@pytest.fixture
def admin_role(db: Session):
    """Create admin role"""
    role = Role(
        name="Admin",
        description="Administrator role",
        is_active=True
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture
def test_user_with_role(db: Session, test_user: User, admin_role: Role):
    """Create test user with admin role"""
    user_role = UserRole(user_id=test_user.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()
    return test_user
