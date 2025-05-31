#!/usr/bin/env python3
"""
Test script to validate AP transaction creation payload
"""
import sys
sys.path.append('.')

from app.schemas.core import APTransactionCreate
from pydantic import ValidationError
from datetime import date
import json

# Test payload similar to what frontend sends
test_payload = {
    "supplier_id": 1,
    "transaction_type_id": 1,
    "accounting_period_id": 1,
    "transaction_date": "2025-06-01",
    "reference_number": "TEST001",
    "description": "Test transaction",
    "gross_amount": 100.00,
    "tax_amount": 0.00,
    "discount_amount": 0.00,
    "source_module": "AP",
    "company_id": 1  # This gets added by the backend
}

print("Testing AP transaction payload validation...")
print(f"Payload: {json.dumps(test_payload, indent=2)}")

try:
    # Convert string date to date object (as FastAPI would do)
    test_payload["transaction_date"] = date.fromisoformat(test_payload["transaction_date"])
    
    # Validate using Pydantic schema
    ap_transaction = APTransactionCreate(**test_payload)
    print("✅ Payload validation successful!")
    print(f"Validated object: {ap_transaction}")
    
except ValidationError as e:
    print("❌ Payload validation failed!")
    print(f"Validation errors: {e}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
