import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date
from app.models.core import GLAccount, GLTransaction, Company, User, AccountingPeriod
from app.schemas.core import GLAccountCreate, GLTransactionCreate
from app.crud.general_ledger import gl_account_crud, gl_transaction_crud


class TestGLAccountCRUD:
    """Test GL Account CRUD operations"""
    
    def test_create_gl_account(self, db: Session, test_company: Company):
        """Test creating a GL account"""
        account_data = GLAccountCreate(
            company_id=test_company.id,
            account_code="1000",
            account_name="Cash",
            account_type="ASSETS",
            account_subtype="Current Assets",
            normal_balance="DEBIT",
            description="Cash account"
        )
        
        account = gl_account_crud.create_account(db, account_data)
        
        assert account.id is not None
        assert account.account_code == "1000"
        assert account.account_name == "Cash"
        assert account.account_type == "ASSETS"
        assert account.normal_balance == "DEBIT"
        assert account.is_active is True
        assert account.company_id == test_company.id
    
    def test_get_account_by_code(self, db: Session, test_company: Company):
        """Test getting account by code"""
        # Create account
        account_data = GLAccountCreate(
            company_id=test_company.id,
            account_code="2000",
            account_name="Accounts Payable",
            account_type="LIABILITIES",
            normal_balance="CREDIT"
        )
        created_account = gl_account_crud.create_account(db, account_data)
        
        # Get by code
        found_account = gl_account_crud.get_account_by_code(db, "2000", test_company.id)
        
        assert found_account is not None
        assert found_account.id == created_account.id
        assert found_account.account_code == "2000"
    
    def test_get_accounts_with_filters(self, db: Session, test_company: Company):
        """Test getting accounts with filters"""
        # Create multiple accounts
        accounts_data = [
            GLAccountCreate(
                company_id=test_company.id,
                account_code="1100",
                account_name="Cash - Checking",
                account_type="ASSETS",
                normal_balance="DEBIT"
            ),
            GLAccountCreate(
                company_id=test_company.id,
                account_code="4000",
                account_name="Sales Revenue",
                account_type="REVENUE",
                normal_balance="CREDIT"
            ),
            GLAccountCreate(
                company_id=test_company.id,
                account_code="1200",
                account_name="Accounts Receivable",
                account_type="ASSETS",
                normal_balance="DEBIT",
                is_active=False
            )
        ]
        
        for account_data in accounts_data:
            gl_account_crud.create_account(db, account_data)
        
        # Test filter by account type
        asset_accounts = gl_account_crud.get_accounts(db, test_company.id, account_type="ASSETS")
        assert len(asset_accounts) >= 2
        
        # Test filter by is_active
        active_accounts = gl_account_crud.get_accounts(db, test_company.id, is_active=True)
        inactive_accounts = gl_account_crud.get_accounts(db, test_company.id, is_active=False)
        
        assert len(active_accounts) >= 2
        assert len(inactive_accounts) >= 1


class TestGLTransactionCRUD:
    """Test GL Transaction CRUD operations"""
    
    def test_create_gl_transaction(self, db: Session, test_company: Company, test_user: User, 
                                 test_accounting_period: AccountingPeriod):
        """Test creating a GL transaction"""
        # Create GL account first
        account_data = GLAccountCreate(
            company_id=test_company.id,
            account_code="1001",
            account_name="Cash",
            account_type="ASSETS",
            normal_balance="DEBIT"
        )
        account = gl_account_crud.create_account(db, account_data)
        
        # Create transaction
        transaction_data = GLTransactionCreate(
            company_id=test_company.id,
            accounting_period_id=test_accounting_period.id,
            gl_account_id=account.id,
            transaction_date=date.today(),
            description="Initial cash deposit",
            debit_amount=1000.00,
            credit_amount=0.00,
            posted_by=test_user.id
        )
        
        transaction = gl_transaction_crud.create_transaction(db, transaction_data)
        
        assert transaction.id is not None
        assert transaction.gl_account_id == account.id
        assert transaction.debit_amount == 1000.00
        assert transaction.credit_amount == 0.00
        assert transaction.description == "Initial cash deposit"
    
    def test_create_transaction_validation(self, db: Session, test_company: Company, test_user: User,
                                         test_accounting_period: AccountingPeriod):
        """Test transaction validation rules"""
        # Create GL account
        account_data = GLAccountCreate(
            company_id=test_company.id,
            account_code="1002",
            account_name="Test Account",
            account_type="ASSETS",
            normal_balance="DEBIT"
        )
        account = gl_account_crud.create_account(db, account_data)
        
        # Test: Both debit and credit amounts
        with pytest.raises(ValueError, match="either a debit amount or credit amount"):
            transaction_data = GLTransactionCreate(
                company_id=test_company.id,
                accounting_period_id=test_accounting_period.id,
                gl_account_id=account.id,
                transaction_date=date.today(),
                description="Invalid transaction",
                debit_amount=100.00,
                credit_amount=50.00,
                posted_by=test_user.id
            )
            gl_transaction_crud.create_transaction(db, transaction_data)
        
        # Test: Neither debit nor credit amounts
        with pytest.raises(ValueError, match="either a debit amount or credit amount"):
            transaction_data = GLTransactionCreate(
                company_id=test_company.id,
                accounting_period_id=test_accounting_period.id,
                gl_account_id=account.id,
                transaction_date=date.today(),
                description="Invalid transaction",
                debit_amount=0.00,
                credit_amount=0.00,
                posted_by=test_user.id
            )
            gl_transaction_crud.create_transaction(db, transaction_data)
    
    def test_trial_balance(self, db: Session, test_company: Company, test_user: User,
                          test_accounting_period: AccountingPeriod):
        """Test trial balance generation"""
        # Create accounts
        cash_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="1000",
            account_name="Cash",
            account_type="ASSETS",
            normal_balance="DEBIT"
        ))
        
        revenue_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="4000",
            account_name="Sales Revenue",
            account_type="REVENUE",
            normal_balance="CREDIT"
        ))
        
        # Create transactions
        gl_transaction_crud.create_transaction(db, GLTransactionCreate(
            company_id=test_company.id,
            accounting_period_id=test_accounting_period.id,
            gl_account_id=cash_account.id,
            transaction_date=date.today(),
            description="Cash receipt",
            debit_amount=1000.00,
            credit_amount=0.00,
            posted_by=test_user.id
        ))
        
        gl_transaction_crud.create_transaction(db, GLTransactionCreate(
            company_id=test_company.id,
            accounting_period_id=test_accounting_period.id,
            gl_account_id=revenue_account.id,
            transaction_date=date.today(),
            description="Sales revenue",
            debit_amount=0.00,
            credit_amount=1000.00,
            posted_by=test_user.id
        ))
        
        # Generate trial balance
        trial_balance = gl_transaction_crud.get_trial_balance(db, test_company.id, test_accounting_period.id)
        
        assert len(trial_balance) == 2
        
        # Find cash account in trial balance
        cash_item = next((item for item in trial_balance if item.account_code == "1000"), None)
        assert cash_item is not None
        assert cash_item.debit_balance == 1000.00
        assert cash_item.credit_balance == 0.00
        
        # Find revenue account in trial balance
        revenue_item = next((item for item in trial_balance if item.account_code == "4000"), None)
        assert revenue_item is not None
        assert revenue_item.debit_balance == 0.00
        assert revenue_item.credit_balance == 1000.00


class TestGeneralLedgerAPI:
    """Test General Ledger API endpoints"""
    
    def test_create_gl_account_api(self, client: TestClient, auth_headers: dict):
        """Test creating GL account via API"""
        account_data = {
            "account_code": "1000",
            "account_name": "Cash",
            "account_type": "ASSETS",
            "normal_balance": "DEBIT",
            "description": "Main cash account"
        }
        
        response = client.post("/api/gl/accounts", json=account_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["account_code"] == "1000"
        assert data["account_name"] == "Cash"
        assert data["account_type"] == "ASSETS"
    
    def test_get_chart_of_accounts_api(self, client: TestClient, auth_headers: dict):
        """Test getting chart of accounts via API"""
        # First create some accounts
        accounts = [
            {
                "account_code": "1100",
                "account_name": "Cash - Checking",
                "account_type": "ASSETS",
                "normal_balance": "DEBIT"
            },
            {
                "account_code": "2000",
                "account_name": "Accounts Payable",
                "account_type": "LIABILITIES",
                "normal_balance": "CREDIT"
            }
        ]
        
        for account in accounts:
            client.post("/api/gl/accounts", json=account, headers=auth_headers)
        
        # Get chart of accounts
        response = client.get("/api/gl/accounts/chart", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert len(data["accounts"]) >= 2
    
    def test_create_gl_transaction_api(self, client: TestClient, auth_headers: dict):
        """Test creating GL transaction via API"""
        # First create an account
        account_data = {
            "account_code": "1001",
            "account_name": "Test Cash Account",
            "account_type": "ASSETS",
            "normal_balance": "DEBIT"
        }
        account_response = client.post("/api/gl/accounts", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Get an accounting period
        periods_response = client.get("/api/accounting-periods", headers=auth_headers)
        periods = periods_response.json()
        if not periods:
            # Create a period if none exists
            period_data = {
                "period_name": "Test Period",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "financial_year": 2025
            }
            period_response = client.post("/api/accounting-periods", json=period_data, headers=auth_headers)
            period_id = period_response.json()["id"]
        else:
            period_id = periods[0]["id"]
        
        # Create transaction
        transaction_data = {
            "accounting_period_id": period_id,
            "gl_account_id": account_id,
            "transaction_date": "2025-05-26",
            "description": "Test transaction",
            "debit_amount": 500.00,
            "credit_amount": 0.00
        }
        
        response = client.post("/api/gl/transactions", json=transaction_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["gl_account_id"] == account_id
        assert data["debit_amount"] == 500.00
        assert data["description"] == "Test transaction"
    
    def test_trial_balance_api(self, client: TestClient, auth_headers: dict):
        """Test trial balance report via API"""
        # Get an accounting period
        periods_response = client.get("/api/accounting-periods", headers=auth_headers)
        periods = periods_response.json()
        if periods:
            period_id = periods[0]["id"]
            
            response = client.get(f"/api/gl/reports/trial-balance/{period_id}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "period_id" in data
            assert "accounts" in data
            assert "total_debits" in data
            assert "total_credits" in data
            assert "is_balanced" in data
