"""
Simple Transaction Behavior Test - Basic Validation

This is a simplified version to validate the test setup works correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date

from main import app
from app.models.core import GLAccount, Company, User
from app.schemas.core import GLAccountCreate
from app.crud.general_ledger import gl_account_crud

client = TestClient(app)


class TestBasicSetup:
    """Basic test to validate setup"""

    def test_basic_gl_account_creation(self, db: Session, test_company: Company):
        """Test basic GL account creation"""
        # Create a simple GL account
        account_data = GLAccountCreate(
            company_id=test_company.id,
            account_code="1000", 
            account_name="Cash",
            account_type="ASSETS",
            normal_balance="DEBIT"
        )
        
        account = gl_account_crud.create_account(db, account_data)
        
        # Basic verifications
        assert account is not None
        assert account.account_code == "1000"
        assert account.account_name == "Cash"
        assert account.company_id == test_company.id
        
        print(f"✓ GL Account created successfully: {account.account_name}")

    def test_company_fixture(self, test_company: Company):
        """Test that company fixture works"""
        assert test_company is not None
        assert test_company.name == "Test Company Ltd"
        print(f"✓ Company fixture works: {test_company.name}")

    def test_user_fixture(self, test_user: User):
        """Test that user fixture works"""
        assert test_user is not None
        assert test_user.username == "testuser"
        print(f"✓ User fixture works: {test_user.username}")

    def test_db_fixture(self, db: Session):
        """Test that database fixture works"""
        assert db is not None
        # Try a simple query
        result = db.execute("SELECT 1").scalar()
        assert result == 1
        print("✓ Database fixture works")
