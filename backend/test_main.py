import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import Company, User, Role
from app.core.security import get_password_hash

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_company():
    """Create a test company"""
    db = TestingSessionLocal()
    company = Company(
        name="Test Company",
        address={"street": "123 Test St"},
        contact_info={"email": "test@test.com"}
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    yield company
    db.close()


@pytest.fixture
def test_user(test_company):
    """Create a test user"""
    db = TestingSessionLocal()
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
    yield user
    db.close()


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "rwanly Core ERP" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        data={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401


class TestUserAPI:
    """Test user-related endpoints"""
    
    def test_get_users_unauthorized(self):
        """Test getting users without authentication"""
        response = client.get("/api/users/")
        assert response.status_code == 401
    
    def test_create_user_unauthorized(self):
        """Test creating user without authentication"""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "company_id": 1
        }
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 401


class TestCompanyAPI:
    """Test company-related endpoints"""
    
    def test_get_companies_unauthorized(self):
        """Test getting companies without authentication"""
        response = client.get("/api/companies/")
        assert response.status_code == 401


class TestRoleAPI:
    """Test role-related endpoints"""
    
    def test_get_roles_unauthorized(self):
        """Test getting roles without authentication"""
        response = client.get("/api/roles/")
        assert response.status_code == 401
