#!/usr/bin/env python3
"""
Test script for Accounts Receivable module functionality
Tests all major AR operations including customers, transactions, and allocations.
"""

import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add the project root to the Python path  
sys.path.append(os.path.dirname(__file__))

from app.database.database import SessionLocal
from app.models.core import Company, User, Customer, ARTransactionType, ARTransaction, ARAllocation
from app.crud.accounts_receivable import (
    customer_crud, ar_transaction_type_crud, ar_transaction_crud, 
    ar_allocation_crud, ar_reporting_crud
)
from app.schemas.core import (
    CustomerCreate, ARTransactionCreate, ARAllocationCreate
)


def test_ar_module():
    """Test all AR module functionality"""
    print("Testing Accounts Receivable Module")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Get test company and user
        company = db.query(Company).filter(Company.is_active == True).first()
        user = db.query(User).filter(User.company_id == company.id).first()
        
        if not company or not user:
            print("Error: No test company or user found!")
            return False
        
        print(f"Using company: {company.name} (ID: {company.id})")
        print(f"Using user: {user.username} (ID: {user.id})")
        print()
        
        # Test 1: Customer Management
        print("1. Testing Customer Management")
        print("-" * 30)
        
        # Create test customer
        customer_data = CustomerCreate(
            company_id=company.id,
            customer_code="CUST001",
            name="Test Customer Ltd",
            contact_person="John Doe",
            email="john@testcustomer.com",
            phone="+1-555-0123", 
            address_line1="123 Business St",
            city="Business City",
            state="Business State",
            postal_code="12345",
            country="United States",
            payment_terms_days=30,
            credit_limit=Decimal("10000.00"),
            is_active=True
        )
        
        customer = customer_crud.create_customer(db, customer_data)
        print(f"✓ Created customer: {customer.customer_code} - {customer.name}")
        
        # Test customer retrieval
        retrieved_customer = customer_crud.get_customer(db, customer.id, company.id)
        assert retrieved_customer.customer_code == "CUST001"
        print("✓ Customer retrieval test passed")
        print()
        
        # Test 2: AR Transaction Types
        print("2. Testing AR Transaction Types")
        print("-" * 30)
        
        transaction_types = ar_transaction_type_crud.get_transaction_types(db, company.id)
        print(f"✓ Found {len(transaction_types)} transaction types")
        
        invoice_type = None
        payment_type = None
        for tt in transaction_types:
            print(f"  - {tt.type_code}: {tt.type_name} ({tt.affects_balance})")
            if tt.type_code == "INV":
                invoice_type = tt
            elif tt.type_code == "PMT":
                payment_type = tt
        
        if not invoice_type or not payment_type:
            print("Error: Required transaction types not found!")
            return False
        print()
        
        # Test 3: AR Transactions
        print("3. Testing AR Transactions")
        print("-" * 30)
        
        # Create test invoice
        invoice_data = ARTransactionCreate(
            company_id=company.id,
            customer_id=customer.id,
            transaction_type_id=invoice_type.id,
            accounting_period_id=1,  # Assuming first period
            transaction_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            reference_number="INV-001",
            description="Test invoice for services",
            gross_amount=1000.00,
            tax_amount=100.00,
            discount_amount=0.00
        )
        
        invoice = ar_transaction_crud.create_transaction(db, invoice_data)
        print(f"✓ Created invoice: {invoice.reference_number} for ${invoice.net_amount}")
        
        # Create test payment
        payment_data = ARTransactionCreate(
            company_id=company.id,
            customer_id=customer.id,
            transaction_type_id=payment_type.id,
            accounting_period_id=1,
            transaction_date=date.today(),
            reference_number="PMT-001", 
            description="Payment for invoice INV-001",
            gross_amount=500.00,
            tax_amount=0.00,
            discount_amount=0.00
        )
        
        payment = ar_transaction_crud.create_transaction(db, payment_data)
        print(f"✓ Created payment: {payment.reference_number} for ${payment.net_amount}")
        
        # Post transactions
        posted_invoice = ar_transaction_crud.post_transaction(db, invoice.id, company.id, user.id)
        posted_payment = ar_transaction_crud.post_transaction(db, payment.id, company.id, user.id)
        print("✓ Posted invoice and payment transactions")
        print()
        
        # Test 4: AR Allocations
        print("4. Testing AR Allocations")
        print("-" * 30)
        
        allocation_data = ARAllocationCreate(
            company_id=company.id,
            customer_id=customer.id,
            transaction_id=payment.id,  # Payment
            allocated_to_id=invoice.id,  # Invoice
            allocation_date=date.today(),
            allocated_amount=500.00,
            reference="Partial payment allocation"
        )
        
        allocation = ar_allocation_crud.create_allocation(db, allocation_data, user.id)
        print(f"✓ Created allocation: ${allocation.allocated_amount} from payment to invoice")
        
        # Verify outstanding amounts updated
        updated_invoice = ar_transaction_crud.get_transaction(db, invoice.id, company.id)
        updated_payment = ar_transaction_crud.get_transaction(db, payment.id, company.id)
        print(f"✓ Invoice outstanding: ${updated_invoice.outstanding_amount}")
        print(f"✓ Payment outstanding: ${updated_payment.outstanding_amount}")
        print()
        
        # Test 5: Customer Aging Report
        print("5. Testing Customer Aging Report")
        print("-" * 30)
        
        aging_report = ar_reporting_crud.generate_customer_ageing_report(db, company.id)
        print(f"✓ Generated aging report with {len(aging_report.customers)} customers")
        
        for customer_aging in aging_report.customers:
            print(f"  - {customer_aging.customer_name}: Total outstanding ${customer_aging.total_outstanding}")
        print()
        
        # Test 6: Customer Transaction Report
        print("6. Testing Customer Transaction Report")
        print("-" * 30)
        
        transaction_report = ar_reporting_crud.generate_customer_transaction_report(
            db, company.id, customer.id
        )
        print(f"✓ Generated transaction report for {transaction_report.customer.name}")
        print(f"  - Total transactions: {transaction_report.summary['transaction_count']}")
        print(f"  - Total gross: ${transaction_report.summary['total_gross']}")
        print(f"  - Total outstanding: ${transaction_report.summary['total_outstanding']}")
        print()
        
        print("🎉 All AR tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Main test function"""
    print("rwanly Core ERP - Accounts Receivable Module Test")
    print("=" * 60)
    print()
    
    success = test_ar_module()
    
    print()
    print("=" * 60)
    if success:
        print("✅ AR Module test completed successfully!")
    else:
        print("❌ AR Module test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
