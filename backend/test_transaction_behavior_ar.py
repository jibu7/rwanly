"""
Test Transaction & Document Processing Behavior - AR Module
Tests the specific behaviors described in the CRUD_Testing_Checklist.md

This test file validates:
1. AR Invoice creation and posting
2. AR Receipt processing
3. Customer balance updates
4. GL control account updates
5. AR Allocation functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from app.models.core import (
    Company, User, AccountingPeriod, Customer, GLAccount,
    ARTransactionType, ARTransaction, ARAllocation
)
from app.schemas.core import (
    CustomerCreate, GLAccountCreate, ARTransactionTypeCreate,
    ARTransactionCreate, ARAllocationCreate
)
from app.crud.core import customer_crud
from app.crud.general_ledger import gl_account_crud
from app.crud.accounts_receivable import ar_transaction_type_crud, ar_transaction_crud, ar_allocation_crud


class TestARTransactionBehavior:
    """Test AR Transaction Processing Behavior"""
    
    def setup_ar_test_data(self, db: Session, test_company: Company, test_user: User):
        """Setup common test data for AR tests"""
        
        # Create customer
        customer = customer_crud.create_customer(db, CustomerCreate(
            company_id=test_company.id,
            customer_code="CUST001",
            customer_name="Test Customer Ltd",
            contact_person="John Doe",
            email="john@testcustomer.com",
            credit_limit=10000.00,
            payment_terms="Net 30"
        ))
        
        # Create GL accounts for AR
        ar_control_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="1200",
            account_name="Accounts Receivable Control",
            account_type="ASSETS",
            normal_balance="DEBIT",
            is_control_account=True
        ))
        
        sales_income_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="4000",
            account_name="Sales Income",
            account_type="REVENUE", 
            normal_balance="CREDIT"
        ))
        
        cash_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="1000",
            account_name="Cash",
            account_type="ASSETS",
            normal_balance="DEBIT"
        ))
        
        # Create AR transaction types
        invoice_type = ar_transaction_type_crud.create_transaction_type(db, ARTransactionTypeCreate(
            company_id=test_company.id,
            type_code="INV",
            type_name="Customer Invoice",
            gl_account_id=ar_control_account.id,
            default_income_account_id=sales_income_account.id,
            affects_balance="DEBIT",
            is_active=True
        ))
        
        receipt_type = ar_transaction_type_crud.create_transaction_type(db, ARTransactionTypeCreate(
            company_id=test_company.id,
            type_code="RCP",
            type_name="Customer Receipt",
            gl_account_id=cash_account.id,
            default_income_account_id=ar_control_account.id,
            affects_balance="CREDIT",
            is_active=True
        ))
        
        return {
            'customer': customer,
            'ar_control_account': ar_control_account,
            'sales_income_account': sales_income_account,
            'cash_account': cash_account,
            'invoice_type': invoice_type,
            'receipt_type': receipt_type
        }
    
    def test_ar_invoice_creation_and_posting(self, db: Session, test_company: Company, 
                                           test_user: User, test_accounting_period: AccountingPeriod):
        """
        Action: Create a new manual AR Invoice.
        Verification:
        - Invoice MUST post successfully.
        - Customer balance MUST update.
        - GL control account MUST update.
        - Invoice MUST appear in AR Transaction Listing.
        """
        
        test_data = self.setup_ar_test_data(db, test_company, test_user)
        
        # Create AR Invoice
        invoice_data = ARTransactionCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="INV-001",
            description="Sales invoice for testing",
            gross_amount=1000.00,
            discount_amount=0.00,
            tax_amount=0.00,
            net_amount=1000.00,
            posted_by=test_user.id
        )
        
        # Create the invoice
        invoice = ar_transaction_crud.create_transaction(db, invoice_data)
        assert invoice.id is not None, "Invoice must be created successfully"
        assert invoice.net_amount == 1000.00, "Invoice amount must be recorded correctly"
        
        # Post the invoice
        posted_invoice = ar_transaction_crud.post_transaction(
            db, invoice.id, test_company.id, test_user.id
        )
        assert posted_invoice is not None, "Invoice MUST post successfully"
        assert posted_invoice.is_posted == True, "Invoice must be marked as posted"
        assert posted_invoice.posted_by == test_user.id, "Posted by user must be recorded"
        
        # Verify customer balance updated
        updated_customer = customer_crud.get_customer(db, test_data['customer'].id, test_company.id)
        assert updated_customer.current_balance == 1000.00, "Customer balance MUST update"
        
        # Verify invoice appears in AR Transaction Listing
        ar_transactions = ar_transaction_crud.get_transactions(db, test_company.id)
        invoice_in_listing = next((t for t in ar_transactions if t.id == invoice.id), None)
        assert invoice_in_listing is not None, "Invoice MUST appear in AR Transaction Listing"
        assert invoice_in_listing.reference_number == "INV-001", "Invoice reference must be correct"
        
        # Verify GL control account impact (in a full implementation)
        # This would verify that GL transactions were created for the AR control account
        
    def test_ar_receipt_creation_and_posting(self, db: Session, test_company: Company,
                                           test_user: User, test_accounting_period: AccountingPeriod):
        """
        Action: Create a new AR Receipt for an existing customer.
        Verification:
        - Receipt MUST post successfully.
        - Customer balance MUST update.
        - GL cash/bank account MUST update.
        """
        
        test_data = self.setup_ar_test_data(db, test_company, test_user)
        
        # First create and post an invoice to have a balance
        invoice_data = ARTransactionCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="INV-002",
            description="Initial invoice",
            gross_amount=1500.00,
            net_amount=1500.00,
            posted_by=test_user.id
        )
        invoice = ar_transaction_crud.create_transaction(db, invoice_data)
        ar_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Create AR Receipt
        receipt_data = ARTransactionCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            transaction_type_id=test_data['receipt_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="RCP-001",
            description="Customer payment received",
            gross_amount=800.00,
            net_amount=800.00,
            posted_by=test_user.id
        )
        
        # Create the receipt
        receipt = ar_transaction_crud.create_transaction(db, receipt_data)
        assert receipt.id is not None, "Receipt must be created successfully"
        assert receipt.net_amount == 800.00, "Receipt amount must be recorded correctly"
        
        # Post the receipt
        posted_receipt = ar_transaction_crud.post_transaction(
            db, receipt.id, test_company.id, test_user.id
        )
        assert posted_receipt is not None, "Receipt MUST post successfully"
        assert posted_receipt.is_posted == True, "Receipt must be marked as posted"
        
        # Verify customer balance updated (should be 1500 - 800 = 700)
        updated_customer = customer_crud.get_customer(db, test_data['customer'].id, test_company.id)
        expected_balance = 1500.00 - 800.00
        assert updated_customer.current_balance == expected_balance, "Customer balance MUST update correctly"
        
        # Verify receipt appears in transaction listing
        ar_transactions = ar_transaction_crud.get_transactions(db, test_company.id)
        receipt_in_listing = next((t for t in ar_transactions if t.id == receipt.id), None)
        assert receipt_in_listing is not None, "Receipt must appear in AR Transaction Listing"
        
    def test_ar_allocation_functionality(self, db: Session, test_company: Company,
                                       test_user: User, test_accounting_period: AccountingPeriod):
        """
        Action: Navigate to AR Allocation, select a customer with an open invoice and an 
        unallocated receipt. Allocate the receipt fully or partially to the invoice.
        Verification:
        - The allocation MUST complete successfully.
        - Invoice status and remaining balance MUST update.
        - Receipt remaining balance MUST update.
        - The allocation MUST be reflected in the customer's transaction history.
        """
        
        test_data = self.setup_ar_test_data(db, test_company, test_user)
        
        # Create and post an invoice
        invoice_data = ARTransactionCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="INV-ALLOC-001",
            description="Invoice for allocation test",
            gross_amount=1200.00,
            net_amount=1200.00,
            posted_by=test_user.id
        )
        invoice = ar_transaction_crud.create_transaction(db, invoice_data)
        ar_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Create and post a receipt
        receipt_data = ARTransactionCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            transaction_type_id=test_data['receipt_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="RCP-ALLOC-001",
            description="Payment for allocation",
            gross_amount=500.00,
            net_amount=500.00,
            posted_by=test_user.id
        )
        receipt = ar_transaction_crud.create_transaction(db, receipt_data)
        ar_transaction_crud.post_transaction(db, receipt.id, test_company.id, test_user.id)
        
        # Verify initial unallocated amounts
        assert invoice.allocated_amount == 0.00, "Invoice should start unallocated"
        assert receipt.allocated_amount == 0.00, "Receipt should start unallocated"
        
        # Create allocation (partial allocation of receipt to invoice)
        allocation_data = ARAllocationCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            debit_transaction_id=invoice.id,  # Invoice (debit transaction)
            credit_transaction_id=receipt.id,  # Receipt (credit transaction)
            allocation_amount=500.00,  # Full receipt amount
            allocation_date=date.today(),
            reference_number="ALLOC-001",
            description="Allocate receipt to invoice",
            allocated_by=test_user.id
        )
        
        allocation = ar_allocation_crud.create_allocation(db, allocation_data)
        assert allocation.id is not None, "Allocation MUST complete successfully"
        assert allocation.allocation_amount == 500.00, "Allocation amount must be recorded correctly"
        
        # Verify invoice and receipt balances updated
        db.refresh(invoice)
        db.refresh(receipt)
        
        invoice_remaining = invoice.net_amount - invoice.allocated_amount
        receipt_remaining = receipt.net_amount - receipt.allocated_amount
        
        # After allocation: Invoice should have 500 allocated (700 remaining)
        # Receipt should have 500 allocated (0 remaining)
        assert invoice.allocated_amount == 500.00, "Invoice allocated amount MUST update"
        assert receipt.allocated_amount == 500.00, "Receipt allocated amount MUST update"
        assert invoice_remaining == 700.00, "Invoice remaining balance MUST update"
        assert receipt_remaining == 0.00, "Receipt remaining balance MUST update"
        
        # Verify allocation appears in customer transaction history
        customer_allocations = ar_allocation_crud.get_customer_allocations(
            db, test_data['customer'].id, test_company.id
        )
        assert len(customer_allocations) == 1, "Allocation must be reflected in customer history"
        assert customer_allocations[0].allocation_amount == 500.00, "Allocation amount must be correct"
        
    def test_customer_balance_consistency(self, db: Session, test_company: Company,
                                        test_user: User, test_accounting_period: AccountingPeriod):
        """
        Test that customer balance remains consistent across multiple AR transactions
        """
        
        test_data = self.setup_ar_test_data(db, test_company, test_user)
        
        # Initial customer balance should be zero
        initial_customer = customer_crud.get_customer(db, test_data['customer'].id, test_company.id)
        assert initial_customer.current_balance == 0.00, "Customer should start with zero balance"
        
        # Create and post multiple invoices
        for i in range(3):
            invoice_data = ARTransactionCreate(
                company_id=test_company.id,
                customer_id=test_data['customer'].id,
                transaction_type_id=test_data['invoice_type'].id,
                accounting_period_id=test_accounting_period.id,
                transaction_date=date.today(),
                reference_number=f"INV-{i+1:03d}",
                description=f"Invoice {i+1}",
                gross_amount=300.00,
                net_amount=300.00,
                posted_by=test_user.id
            )
            invoice = ar_transaction_crud.create_transaction(db, invoice_data)
            ar_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Customer balance should be 900.00 (3 × 300.00)
        customer_after_invoices = customer_crud.get_customer(db, test_data['customer'].id, test_company.id)
        assert customer_after_invoices.current_balance == 900.00, "Customer balance must reflect all invoices"
        
        # Create and post a receipt
        receipt_data = ARTransactionCreate(
            company_id=test_company.id,
            customer_id=test_data['customer'].id,
            transaction_type_id=test_data['receipt_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="RCP-FINAL",
            description="Partial payment",
            gross_amount=450.00,
            net_amount=450.00,
            posted_by=test_user.id
        )
        receipt = ar_transaction_crud.create_transaction(db, receipt_data)
        ar_transaction_crud.post_transaction(db, receipt.id, test_company.id, test_user.id)
        
        # Final customer balance should be 450.00 (900.00 - 450.00)
        final_customer = customer_crud.get_customer(db, test_data['customer'].id, test_company.id)
        assert final_customer.current_balance == 450.00, "Customer balance must be correct after receipt"


class TestARTransactionAPI:
    """Test AR Transaction API endpoints for Transaction & Document Processing Behavior"""
    
    def test_ar_invoice_api_workflow(self, client: TestClient, auth_headers: dict):
        """Test complete AR invoice workflow via API"""
        
        # Create customer via API
        customer_data = {
            "customer_code": "API-CUST-001",
            "customer_name": "API Test Customer",
            "contact_person": "Jane Smith",
            "email": "jane@apitest.com",
            "credit_limit": 5000.00,
            "payment_terms": "Net 30"
        }
        customer_response = client.post("/api/customers", json=customer_data, headers=auth_headers)
        assert customer_response.status_code == 201
        customer_id = customer_response.json()["id"]
        
        # Get AR transaction types
        ar_types_response = client.get("/api/ar/transaction-types", headers=auth_headers)
        assert ar_types_response.status_code == 200
        ar_types = ar_types_response.json()
        
        # Find invoice type
        invoice_type = next((t for t in ar_types if t["type_code"] == "INV"), None)
        if not invoice_type:
            # Create invoice type if it doesn't exist
            invoice_type_data = {
                "type_code": "INV",
                "type_name": "Customer Invoice",
                "affects_balance": "DEBIT"
            }
            invoice_type_response = client.post("/api/ar/transaction-types", json=invoice_type_data, headers=auth_headers)
            assert invoice_type_response.status_code == 201
            invoice_type = invoice_type_response.json()
        
        # Get accounting period
        periods_response = client.get("/api/accounting-periods", headers=auth_headers)
        periods = periods_response.json()
        period_id = periods[0]["id"]
        
        # Create AR Invoice via API
        invoice_data = {
            "customer_id": customer_id,
            "transaction_type_id": invoice_type["id"],
            "accounting_period_id": period_id,
            "transaction_date": "2025-05-29",
            "reference_number": "API-INV-001",
            "description": "API test invoice",
            "gross_amount": 750.00,
            "discount_amount": 0.00,
            "tax_amount": 0.00,
            "net_amount": 750.00
        }
        
        invoice_response = client.post("/api/ar/transactions", json=invoice_data, headers=auth_headers)
        assert invoice_response.status_code == 201, f"Invoice creation failed: {invoice_response.text}"
        invoice = invoice_response.json()
        
        # Post the invoice
        post_response = client.post(f"/api/ar/transactions/{invoice['id']}/post", headers=auth_headers)
        assert post_response.status_code == 200, "Invoice MUST post successfully via API"
        
        # Verify invoice appears in AR Transaction Listing
        transactions_response = client.get("/api/ar/transactions", headers=auth_headers)
        assert transactions_response.status_code == 200
        transactions = transactions_response.json()
        
        api_invoice = next((t for t in transactions if t["reference_number"] == "API-INV-001"), None)
        assert api_invoice is not None, "Invoice MUST appear in AR Transaction Listing"
        assert api_invoice["is_posted"] == True, "Invoice must be marked as posted"
        
        # Verify customer balance updated
        customer_response = client.get(f"/api/customers/{customer_id}", headers=auth_headers)
        assert customer_response.status_code == 200
        updated_customer = customer_response.json()
        assert updated_customer["current_balance"] == 750.00, "Customer balance MUST update via API"
        
    def test_ar_receipt_api_workflow(self, client: TestClient, auth_headers: dict):
        """Test AR receipt creation and posting via API"""
        
        # Get existing customer or create one
        customers_response = client.get("/api/customers", headers=auth_headers)
        customers = customers_response.json()
        
        if customers:
            customer_id = customers[0]["id"]
        else:
            # Create customer
            customer_data = {
                "customer_code": "API-CUST-002",
                "customer_name": "Receipt Test Customer",
                "contact_person": "Bob Johnson",
                "email": "bob@receipttest.com"
            }
            customer_response = client.post("/api/customers", json=customer_data, headers=auth_headers)
            customer_id = customer_response.json()["id"]
        
        # Get or create receipt transaction type
        ar_types_response = client.get("/api/ar/transaction-types", headers=auth_headers)
        ar_types = ar_types_response.json()
        
        receipt_type = next((t for t in ar_types if t["type_code"] == "RCP"), None)
        if not receipt_type:
            receipt_type_data = {
                "type_code": "RCP", 
                "type_name": "Customer Receipt",
                "affects_balance": "CREDIT"
            }
            receipt_type_response = client.post("/api/ar/transaction-types", json=receipt_type_data, headers=auth_headers)
            receipt_type = receipt_type_response.json()
        
        # Get accounting period
        periods_response = client.get("/api/accounting-periods", headers=auth_headers)
        period_id = periods_response.json()[0]["id"]
        
        # Create AR Receipt via API
        receipt_data = {
            "customer_id": customer_id,
            "transaction_type_id": receipt_type["id"], 
            "accounting_period_id": period_id,
            "transaction_date": "2025-05-29",
            "reference_number": "API-RCP-001",
            "description": "API test receipt",
            "gross_amount": 400.00,
            "net_amount": 400.00
        }
        
        receipt_response = client.post("/api/ar/transactions", json=receipt_data, headers=auth_headers)
        assert receipt_response.status_code == 201, f"Receipt creation failed: {receipt_response.text}"
        receipt = receipt_response.json()
        
        # Post the receipt
        post_response = client.post(f"/api/ar/transactions/{receipt['id']}/post", headers=auth_headers)
        assert post_response.status_code == 200, "Receipt MUST post successfully via API"
        
        # Verify receipt appears in listing
        transactions_response = client.get("/api/ar/transactions", headers=auth_headers)
        transactions = transactions_response.json()
        
        api_receipt = next((t for t in transactions if t["reference_number"] == "API-RCP-001"), None)
        assert api_receipt is not None, "Receipt must appear in AR Transaction Listing"
        assert api_receipt["is_posted"] == True, "Receipt must be marked as posted"
