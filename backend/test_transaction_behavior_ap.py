"""
Test Transaction & Document Processing Behavior - AP Module
Tests the specific behaviors described in the CRUD_Testing_Checklist.md

This test file validates:
1. AP Invoice creation and posting
2. AP Payment processing
3. Supplier balance updates
4. GL control account updates
5. AP Allocation functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from app.models.core import (
    Company, User, AccountingPeriod, Supplier, GLAccount,
    APTransactionType, APTransaction, APAllocation
)
from app.schemas.core import (
    SupplierCreate, GLAccountCreate, APTransactionTypeCreate,
    APTransactionCreate, APAllocationCreate
)
from app.crud.core import supplier_crud
from app.crud.general_ledger import gl_account_crud
from app.crud.accounts_payable import ap_transaction_type_crud, ap_transaction_crud, ap_allocation_crud


class TestAPTransactionBehavior:
    """Test AP Transaction Processing Behavior"""
    
    def setup_ap_test_data(self, db: Session, test_company: Company, test_user: User):
        """Setup common test data for AP tests"""
        
        # Create supplier
        supplier = supplier_crud.create_supplier(db, SupplierCreate(
            company_id=test_company.id,
            supplier_code="SUPP001",
            supplier_name="Test Supplier Ltd",
            contact_person="Alice Brown",
            email="alice@testsupplier.com",
            payment_terms="Net 30",
            is_active=True
        ))
        
        # Create GL accounts for AP
        ap_control_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="2100",
            account_name="Accounts Payable Control",
            account_type="LIABILITIES",
            normal_balance="CREDIT",
            is_control_account=True
        ))
        
        expense_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="5000",
            account_name="Office Expenses",
            account_type="EXPENSES",
            normal_balance="DEBIT"
        ))
        
        cash_account = gl_account_crud.create_account(db, GLAccountCreate(
            company_id=test_company.id,
            account_code="1000",
            account_name="Cash",
            account_type="ASSETS",
            normal_balance="DEBIT"
        ))
        
        # Create AP transaction types
        invoice_type = ap_transaction_type_crud.create_transaction_type(db, APTransactionTypeCreate(
            company_id=test_company.id,
            type_code="INV",
            type_name="Supplier Invoice",
            gl_account_id=ap_control_account.id,
            default_expense_account_id=expense_account.id,
            affects_balance="CREDIT",
            is_active=True
        ))
        
        payment_type = ap_transaction_type_crud.create_transaction_type(db, APTransactionTypeCreate(
            company_id=test_company.id,
            type_code="PAY",
            type_name="Supplier Payment",
            gl_account_id=ap_control_account.id,
            default_expense_account_id=cash_account.id,
            affects_balance="DEBIT",
            is_active=True
        ))
        
        return {
            'supplier': supplier,
            'ap_control_account': ap_control_account,
            'expense_account': expense_account,
            'cash_account': cash_account,
            'invoice_type': invoice_type,
            'payment_type': payment_type
        }
    
    def test_ap_invoice_creation_and_posting(self, db: Session, test_company: Company,
                                           test_user: User, test_accounting_period: AccountingPeriod):
        """
        Action: Create a new manual AP Invoice.
        Verification:
        - Invoice MUST post successfully.
        - Supplier balance MUST update.
        - GL control account MUST update.
        - Invoice MUST appear in AP Transaction Listing.
        """
        
        test_data = self.setup_ap_test_data(db, test_company, test_user)
        
        # Create AP Invoice
        invoice_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-INV-001",
            description="Office supplies purchase",
            gross_amount=800.00,
            discount_amount=0.00,
            tax_amount=0.00,
            net_amount=800.00,
            posted_by=test_user.id
        )
        
        # Create the invoice
        invoice = ap_transaction_crud.create_transaction(db, invoice_data)
        assert invoice.id is not None, "AP Invoice must be created successfully"
        assert invoice.net_amount == 800.00, "Invoice amount must be recorded correctly"
        
        # Post the invoice
        posted_invoice = ap_transaction_crud.post_transaction(
            db, invoice.id, test_company.id, test_user.id
        )
        assert posted_invoice is not None, "AP Invoice MUST post successfully"
        assert posted_invoice.is_posted == True, "Invoice must be marked as posted"
        assert posted_invoice.posted_by == test_user.id, "Posted by user must be recorded"
        
        # Verify supplier balance updated
        updated_supplier = supplier_crud.get_supplier(db, test_data['supplier'].id, test_company.id)
        assert updated_supplier.current_balance == 800.00, "Supplier balance MUST update"
        
        # Verify invoice appears in AP Transaction Listing
        ap_transactions = ap_transaction_crud.get_transactions(db, test_company.id)
        invoice_in_listing = next((t for t in ap_transactions if t.id == invoice.id), None)
        assert invoice_in_listing is not None, "Invoice MUST appear in AP Transaction Listing"
        assert invoice_in_listing.reference_number == "AP-INV-001", "Invoice reference must be correct"
        
    def test_ap_payment_creation_and_posting(self, db: Session, test_company: Company,
                                           test_user: User, test_accounting_period: AccountingPeriod):
        """
        Action: Create a new AP Payment for an existing supplier.
        Verification:
        - Payment MUST post successfully.
        - Supplier balance MUST update.
        - GL cash/bank account MUST update.
        """
        
        test_data = self.setup_ap_test_data(db, test_company, test_user)
        
        # First create and post an invoice to have a balance
        invoice_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-INV-002",
            description="Initial supplier invoice",
            gross_amount=1200.00,
            net_amount=1200.00,
            posted_by=test_user.id
        )
        invoice = ap_transaction_crud.create_transaction(db, invoice_data)
        ap_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Create AP Payment
        payment_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['payment_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-PAY-001",
            description="Payment to supplier",
            gross_amount=600.00,
            net_amount=600.00,
            posted_by=test_user.id
        )
        
        # Create the payment
        payment = ap_transaction_crud.create_transaction(db, payment_data)
        assert payment.id is not None, "Payment must be created successfully"
        assert payment.net_amount == 600.00, "Payment amount must be recorded correctly"
        
        # Post the payment
        posted_payment = ap_transaction_crud.post_transaction(
            db, payment.id, test_company.id, test_user.id
        )
        assert posted_payment is not None, "Payment MUST post successfully"
        assert posted_payment.is_posted == True, "Payment must be marked as posted"
        
        # Verify supplier balance updated (should be 1200 - 600 = 600)
        updated_supplier = supplier_crud.get_supplier(db, test_data['supplier'].id, test_company.id)
        expected_balance = 1200.00 - 600.00
        assert updated_supplier.current_balance == expected_balance, "Supplier balance MUST update correctly"
        
        # Verify payment appears in transaction listing
        ap_transactions = ap_transaction_crud.get_transactions(db, test_company.id)
        payment_in_listing = next((t for t in ap_transactions if t.id == payment.id), None)
        assert payment_in_listing is not None, "Payment must appear in AP Transaction Listing"
        
    def test_ap_allocation_functionality(self, db: Session, test_company: Company,
                                       test_user: User, test_accounting_period: AccountingPeriod):
        """
        Action: Navigate to AP Allocation, select a supplier with an open invoice and an
        unallocated payment. Allocate the payment fully or partially to the invoice.
        Verification:
        - The allocation MUST complete successfully.
        - Invoice status and remaining balance MUST update.
        - Payment remaining balance MUST update.
        - The allocation MUST be reflected in the supplier's transaction history.
        """
        
        test_data = self.setup_ap_test_data(db, test_company, test_user)
        
        # Create and post an invoice
        invoice_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-ALLOC-INV-001",
            description="Invoice for allocation test",
            gross_amount=1500.00,
            net_amount=1500.00,
            posted_by=test_user.id
        )
        invoice = ap_transaction_crud.create_transaction(db, invoice_data)
        ap_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Create and post a payment
        payment_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['payment_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-ALLOC-PAY-001",
            description="Payment for allocation",
            gross_amount=700.00,
            net_amount=700.00,
            posted_by=test_user.id
        )
        payment = ap_transaction_crud.create_transaction(db, payment_data)
        ap_transaction_crud.post_transaction(db, payment.id, test_company.id, test_user.id)
        
        # Verify initial unallocated amounts
        assert invoice.allocated_amount == 0.00, "Invoice should start unallocated"
        assert payment.allocated_amount == 0.00, "Payment should start unallocated"
        
        # Create allocation (partial allocation of payment to invoice)
        allocation_data = APAllocationCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            credit_transaction_id=invoice.id,  # Invoice (credit transaction)
            debit_transaction_id=payment.id,   # Payment (debit transaction)
            allocation_amount=700.00,  # Full payment amount
            allocation_date=date.today(),
            reference_number="AP-ALLOC-001",
            description="Allocate payment to invoice",
            allocated_by=test_user.id
        )
        
        allocation = ap_allocation_crud.create_allocation(db, allocation_data)
        assert allocation.id is not None, "Allocation MUST complete successfully"
        assert allocation.allocation_amount == 700.00, "Allocation amount must be recorded correctly"
        
        # Verify invoice and payment balances updated
        db.refresh(invoice)
        db.refresh(payment)
        
        invoice_remaining = invoice.net_amount - invoice.allocated_amount
        payment_remaining = payment.net_amount - payment.allocated_amount
        
        # After allocation: Invoice should have 700 allocated (800 remaining)
        # Payment should have 700 allocated (0 remaining)
        assert invoice.allocated_amount == 700.00, "Invoice allocated amount MUST update"
        assert payment.allocated_amount == 700.00, "Payment allocated amount MUST update"
        assert invoice_remaining == 800.00, "Invoice remaining balance MUST update"
        assert payment_remaining == 0.00, "Payment remaining balance MUST update"
        
        # Verify allocation appears in supplier transaction history
        supplier_allocations = ap_allocation_crud.get_supplier_allocations(
            db, test_data['supplier'].id, test_company.id
        )
        assert len(supplier_allocations) == 1, "Allocation must be reflected in supplier history"
        assert supplier_allocations[0].allocation_amount == 700.00, "Allocation amount must be correct"
        
    def test_supplier_balance_consistency(self, db: Session, test_company: Company,
                                        test_user: User, test_accounting_period: AccountingPeriod):
        """
        Test that supplier balance remains consistent across multiple AP transactions
        """
        
        test_data = self.setup_ap_test_data(db, test_company, test_user)
        
        # Initial supplier balance should be zero
        initial_supplier = supplier_crud.get_supplier(db, test_data['supplier'].id, test_company.id)
        assert initial_supplier.current_balance == 0.00, "Supplier should start with zero balance"
        
        # Create and post multiple invoices
        for i in range(3):
            invoice_data = APTransactionCreate(
                company_id=test_company.id,
                supplier_id=test_data['supplier'].id,
                transaction_type_id=test_data['invoice_type'].id,
                accounting_period_id=test_accounting_period.id,
                transaction_date=date.today(),
                reference_number=f"AP-INV-{i+1:03d}",
                description=f"Supplier Invoice {i+1}",
                gross_amount=400.00,
                net_amount=400.00,
                posted_by=test_user.id
            )
            invoice = ap_transaction_crud.create_transaction(db, invoice_data)
            ap_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Supplier balance should be 1200.00 (3 × 400.00)
        supplier_after_invoices = supplier_crud.get_supplier(db, test_data['supplier'].id, test_company.id)
        assert supplier_after_invoices.current_balance == 1200.00, "Supplier balance must reflect all invoices"
        
        # Create and post a payment
        payment_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['payment_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-PAY-FINAL",
            description="Partial payment",
            gross_amount=500.00,
            net_amount=500.00,
            posted_by=test_user.id
        )
        payment = ap_transaction_crud.create_transaction(db, payment_data)
        ap_transaction_crud.post_transaction(db, payment.id, test_company.id, test_user.id)
        
        # Final supplier balance should be 700.00 (1200.00 - 500.00)
        final_supplier = supplier_crud.get_supplier(db, test_data['supplier'].id, test_company.id)
        assert final_supplier.current_balance == 700.00, "Supplier balance must be correct after payment"
        
    def test_ap_credit_note_processing(self, db: Session, test_company: Company,
                                     test_user: User, test_accounting_period: AccountingPeriod):
        """
        Test AP Credit Note creation and processing behavior
        """
        
        test_data = self.setup_ap_test_data(db, test_company, test_user)
        
        # Create credit note transaction type
        credit_note_type = ap_transaction_type_crud.create_transaction_type(db, APTransactionTypeCreate(
            company_id=test_company.id,
            type_code="CN",
            type_name="Supplier Credit Note",
            gl_account_id=test_data['ap_control_account'].id,
            default_expense_account_id=test_data['expense_account'].id,
            affects_balance="DEBIT",  # Credit notes reduce supplier balance
            is_active=True
        ))
        
        # First create and post an invoice
        invoice_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=test_data['invoice_type'].id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-INV-CN-001",
            description="Invoice for credit note test",
            gross_amount=1000.00,
            net_amount=1000.00,
            posted_by=test_user.id
        )
        invoice = ap_transaction_crud.create_transaction(db, invoice_data)
        ap_transaction_crud.post_transaction(db, invoice.id, test_company.id, test_user.id)
        
        # Create and post a credit note
        credit_note_data = APTransactionCreate(
            company_id=test_company.id,
            supplier_id=test_data['supplier'].id,
            transaction_type_id=credit_note_type.id,
            accounting_period_id=test_accounting_period.id,
            transaction_date=date.today(),
            reference_number="AP-CN-001",
            description="Returned goods credit note",
            gross_amount=200.00,
            net_amount=200.00,
            posted_by=test_user.id
        )
        credit_note = ap_transaction_crud.create_transaction(db, credit_note_data)
        posted_credit_note = ap_transaction_crud.post_transaction(
            db, credit_note.id, test_company.id, test_user.id
        )
        
        assert posted_credit_note.is_posted == True, "Credit note must post successfully"
        
        # Verify supplier balance updated (1000 - 200 = 800)
        updated_supplier = supplier_crud.get_supplier(db, test_data['supplier'].id, test_company.id)
        assert updated_supplier.current_balance == 800.00, "Supplier balance must decrease with credit note"


class TestAPTransactionAPI:
    """Test AP Transaction API endpoints for Transaction & Document Processing Behavior"""
    
    def test_ap_invoice_api_workflow(self, client: TestClient, auth_headers: dict):
        """Test complete AP invoice workflow via API"""
        
        # Create supplier via API
        supplier_data = {
            "supplier_code": "API-SUPP-001",
            "supplier_name": "API Test Supplier",
            "contact_person": "David Wilson",
            "email": "david@apitest.com",
            "payment_terms": "Net 30"
        }
        supplier_response = client.post("/api/suppliers", json=supplier_data, headers=auth_headers)
        assert supplier_response.status_code == 201
        supplier_id = supplier_response.json()["id"]
        
        # Get AP transaction types
        ap_types_response = client.get("/api/ap/transaction-types", headers=auth_headers)
        assert ap_types_response.status_code == 200
        ap_types = ap_types_response.json()
        
        # Find invoice type
        invoice_type = next((t for t in ap_types if t["type_code"] == "INV"), None)
        if not invoice_type:
            # Create invoice type if it doesn't exist
            invoice_type_data = {
                "type_code": "INV",
                "type_name": "Supplier Invoice",
                "affects_balance": "CREDIT"
            }
            invoice_type_response = client.post("/api/ap/transaction-types", json=invoice_type_data, headers=auth_headers)
            assert invoice_type_response.status_code == 201
            invoice_type = invoice_type_response.json()
        
        # Get accounting period
        periods_response = client.get("/api/accounting-periods", headers=auth_headers)
        periods = periods_response.json()
        period_id = periods[0]["id"]
        
        # Create AP Invoice via API
        invoice_data = {
            "supplier_id": supplier_id,
            "transaction_type_id": invoice_type["id"],
            "accounting_period_id": period_id,
            "transaction_date": "2025-05-29",
            "reference_number": "API-AP-INV-001",
            "description": "API test supplier invoice",
            "gross_amount": 950.00,
            "discount_amount": 0.00,
            "tax_amount": 0.00,
            "net_amount": 950.00
        }
        
        invoice_response = client.post("/api/ap/transactions", json=invoice_data, headers=auth_headers)
        assert invoice_response.status_code == 201, f"Invoice creation failed: {invoice_response.text}"
        invoice = invoice_response.json()
        
        # Post the invoice
        post_response = client.post(f"/api/ap/transactions/{invoice['id']}/post", headers=auth_headers)
        assert post_response.status_code == 200, "Invoice MUST post successfully via API"
        
        # Verify invoice appears in AP Transaction Listing
        transactions_response = client.get("/api/ap/transactions", headers=auth_headers)
        assert transactions_response.status_code == 200
        transactions = transactions_response.json()
        
        api_invoice = next((t for t in transactions if t["reference_number"] == "API-AP-INV-001"), None)
        assert api_invoice is not None, "Invoice MUST appear in AP Transaction Listing"
        assert api_invoice["is_posted"] == True, "Invoice must be marked as posted"
        
        # Verify supplier balance updated
        supplier_response = client.get(f"/api/suppliers/{supplier_id}", headers=auth_headers)
        assert supplier_response.status_code == 200
        updated_supplier = supplier_response.json()
        assert updated_supplier["current_balance"] == 950.00, "Supplier balance MUST update via API"
        
    def test_ap_payment_api_workflow(self, client: TestClient, auth_headers: dict):
        """Test AP payment creation and posting via API"""
        
        # Get existing supplier or create one
        suppliers_response = client.get("/api/suppliers", headers=auth_headers)
        suppliers = suppliers_response.json()
        
        if suppliers:
            supplier_id = suppliers[0]["id"]
        else:
            # Create supplier
            supplier_data = {
                "supplier_code": "API-SUPP-002",
                "supplier_name": "Payment Test Supplier",
                "contact_person": "Carol Taylor",
                "email": "carol@paymenttest.com"
            }
            supplier_response = client.post("/api/suppliers", json=supplier_data, headers=auth_headers)
            supplier_id = supplier_response.json()["id"]
        
        # Get or create payment transaction type
        ap_types_response = client.get("/api/ap/transaction-types", headers=auth_headers)
        ap_types = ap_types_response.json()
        
        payment_type = next((t for t in ap_types if t["type_code"] == "PAY"), None)
        if not payment_type:
            payment_type_data = {
                "type_code": "PAY",
                "type_name": "Supplier Payment",
                "affects_balance": "DEBIT"
            }
            payment_type_response = client.post("/api/ap/transaction-types", json=payment_type_data, headers=auth_headers)
            payment_type = payment_type_response.json()
        
        # Get accounting period
        periods_response = client.get("/api/accounting-periods", headers=auth_headers)
        period_id = periods_response.json()[0]["id"]
        
        # Create AP Payment via API
        payment_data = {
            "supplier_id": supplier_id,
            "transaction_type_id": payment_type["id"],
            "accounting_period_id": period_id,
            "transaction_date": "2025-05-29",
            "reference_number": "API-AP-PAY-001",
            "description": "API test payment",
            "gross_amount": 600.00,
            "net_amount": 600.00
        }
        
        payment_response = client.post("/api/ap/transactions", json=payment_data, headers=auth_headers)
        assert payment_response.status_code == 201, f"Payment creation failed: {payment_response.text}"
        payment = payment_response.json()
        
        # Post the payment
        post_response = client.post(f"/api/ap/transactions/{payment['id']}/post", headers=auth_headers)
        assert post_response.status_code == 200, "Payment MUST post successfully via API"
        
        # Verify payment appears in listing
        transactions_response = client.get("/api/ap/transactions", headers=auth_headers)
        transactions = transactions_response.json()
        
        api_payment = next((t for t in transactions if t["reference_number"] == "API-AP-PAY-001"), None)
        assert api_payment is not None, "Payment must appear in AP Transaction Listing"
        assert api_payment["is_posted"] == True, "Payment must be marked as posted"
