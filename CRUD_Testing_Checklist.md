# CRUD Testing Checklist for rwanly Core ERP

## Test Environment Setup
- Backend: FastAPI running at http://localhost:8000
- Frontend: Next.js app

## Login Credentials
- Administrator: admin@techflow.com / admin123
- Accountant: accountant@techflow.com / accountant123
- Sales: sales@techflow.com / sales123
- Clerk: clerk@techflow.com / clerk123

## Testing Approach
For each module, we'll verify:
1. List View (Read)
2. Create Operation
3. Detail/Edit View (Read & Update)
4. Delete Operation

## Modules to Test

### 1. Users Module ✅
- [x] List View: Successfully retrieved all users
- [x] Create: Successfully created a new user
- [x] Edit: Successfully updated a user
- [x] Delete: Successfully deleted a user

### 2. Roles Module ✅
- [x] List View: Successfully retrieved all roles
- [x] Create: Successfully created a new role
- [x] Edit: Successfully updated a role
- [x] Delete: Successfully deleted a role

### 3. Companies Module ✅
- [x] List View: Successfully retrieved all companies
- [x] Create: Successfully created a new company
- [x] Edit: Successfully updated a company
- [x] Delete: Not allowed (by design)

### 4. GL Accounts Module ✅
- [x] List View: Successfully retrieved all GL accounts
- [x] Create: Successfully created a new GL account
- [x] Edit: Successfully updated a GL account (fixed permission handler)
- [x] Delete: Successfully deleted a GL account (fixed permission handler)

### 5. Customers Module ✅
- [x] List View: Successfully retrieved all customers
- [x] Create: Successfully created a new customer
- [x] Edit: Successfully updated a customer
- [x] Delete: Customer is marked as inactive instead of being deleted (soft delete)

### 6. Suppliers Module ✅
- [x] List View: Successfully retrieved all suppliers
- [x] Create: Successfully created a new supplier
- [x] Edit: Successfully updated a supplier
- [x] Delete: Successfully deleted a supplier (hard delete)

### 7. Inventory Items Module ⚠️
- [~] List View: Endpoint exists but returns empty array (placeholder implementation)
- [~] Create: Endpoint exists but returns placeholder message
- [~] Edit: Endpoint exists but returns placeholder message
- [~] Delete: Endpoint exists but returns placeholder message "Inventory item deletion - coming soon"

### 8. Journal Entries Module
- [~] List View: Endpoint exists at /api/gl/transactions but testing revealed no existing entries
- [~] Create: API endpoint exists at /api/gl/transactions but returns Internal Server Error during testing
- [~] Edit: Endpoint should be at /api/gl/transactions/{id} but not tested due to create failures
- [~] Delete: Not tested due to create failures

### 9. AR Transactions/Allocations Module
- [~] List View: API endpoint exists at /api/ar/transactions but returns empty array during testing
- [~] Create: API endpoint exists at /api/ar/transactions but couldn't be tested due to dependency issues
- [~] Edit: API endpoint exists at /api/ar/transactions/{id} but couldn't be tested
- [~] Allocations: API endpoints exist at /api/ar/allocations but couldn't be tested

### 10. AP Transactions/Allocations Module
- [~] List View: API endpoint exists at /api/ap/transactions but returns empty array during testing
- [~] Create: API endpoint exists at /api/ap/transactions but couldn't be tested due to dependency issues
- [~] Edit: API endpoint exists at /api/ap/transactions/{id} but couldn't be tested
- [~] Allocations: API endpoints exist at /api/ap/allocations but couldn't be tested

### 11. OE Documents Module
- [~] List View: API endpoints exist at /api/oe/document-types and /api/oe/sales-orders but return empty arrays during testing
- [~] Create: API endpoints exist at /api/oe/document-types and /api/oe/sales-orders but couldn't be tested due to dependency issues
- [~] Edit: API endpoints exist for updating document types and sales orders but couldn't be tested
- [~] Delete: API endpoints exist for deleting document types and sales orders but couldn't be tested

## Testing Details for Each Module

### List View Test Steps
1. Navigate to the list page
2. Verify data loads correctly
3. Test pagination (if implemented)
4. Test sorting by different columns
5. Test filtering/search functionality
6. Verify all relevant data fields are displayed

### Create Test Steps
1. Navigate to create form
2. Fill in valid data and submit
3. Verify success message
4. Verify new record appears in list
5. Test validation by submitting invalid data:
   - Empty required fields
   - Invalid formats
   - Duplicate unique values

### Edit Test Steps
1. Select an existing record to edit
2. Verify form loads with correct data
3. Make changes and save
4. Verify changes are reflected
5. Test validation rules (same as create)

### Delete Test Steps
1. Attempt to delete a record
2. Verify confirmation prompt
3. Confirm deletion and check if removed
4. Test deletion with dependencies:
   - Try to delete a record with dependencies
   - Verify proper error message or handling

## Transaction & Document Processing Behavior Tests

### Overview
This section covers comprehensive testing of transaction behaviors and document processing workflows. These tests validate that the system correctly handles complex business processes beyond basic CRUD operations.

### Test Files Created
- `test_transaction_behavior_gl.py` - General Ledger transaction behavior tests
- `test_transaction_behavior_ar.py` - Accounts Receivable transaction behavior tests  
- `test_transaction_behavior_ap.py` - Accounts Payable transaction behavior tests
- `test_transaction_behavior_inventory.py` - Inventory adjustment behavior tests
- `test_transaction_behavior_orders.py` - Order entry documents behavior tests

### 1. Journal Entry (GL) Behavior Tests

#### Test Coverage
- **Balanced Journal Entries**: Multi-line entries with balanced debits/credits
- **Unbalanced Entry Prevention**: System prevents posting unbalanced entries
- **Closed Period Validation**: Prevents posting to closed accounting periods
- **GL Account Balance Updates**: Immediate balance updates after posting
- **Transaction Validation Rules**: Validates debit/credit validation rules

#### Key Test Methods
- `test_create_balanced_journal_entry()` - Validates 2+ line balanced entries
- `test_unbalanced_journal_entry_prevention()` - Tests system prevention
- `test_closed_period_posting_prevention()` - Tests period validation
- `test_gl_account_balance_updates()` - Validates balance calculations

### 2. AR Transactions Behavior Tests

#### Test Coverage
- **AR Invoice Processing**: Creation, posting, customer balance updates
- **AR Receipt Processing**: Receipt creation and GL cash account updates
- **AR Allocation**: Payment allocation to invoices with balance tracking
- **Customer Balance Consistency**: Balance validation across transactions
- **API Workflow Testing**: Complete AR transaction workflows via API

#### Key Test Methods
- `test_ar_invoice_creation_and_posting()` - Invoice processing workflow
- `test_ar_receipt_creation_and_posting()` - Receipt processing workflow
- `test_ar_allocation_functionality()` - Payment allocation testing
- `test_customer_balance_consistency()` - Balance validation testing

### 3. AP Transactions Behavior Tests

#### Test Coverage
- **AP Invoice Processing**: Supplier invoice creation and posting
- **AP Payment Processing**: Payment creation and GL account updates
- **AP Allocation**: Payment allocation to supplier invoices
- **Supplier Balance Consistency**: Balance validation across transactions
- **Credit Note Processing**: Credit note handling and balance adjustments

#### Key Test Methods
- `test_ap_invoice_creation_and_posting()` - Supplier invoice workflow
- `test_ap_payment_creation_and_posting()` - Payment processing workflow
- `test_ap_allocation_functionality()` - Payment allocation testing
- `test_supplier_balance_consistency()` - Balance validation testing
- `test_ap_credit_note_processing()` - Credit note processing

### 4. Inventory Adjustment Behavior Tests

#### Test Coverage
- **Adjustment Processing**: "Adjustment Increase" and "Adjustment Decrease"
- **Quantity Updates**: Verify Quantity On Hand updates correctly
- **Inventory Listings**: Verify adjustments appear in listing
- **GL Impact**: Inventory Asset Account and Cost of Sales/Adjustment Account updates
- **Validation Rules**: Prevent negative quantities and zero adjustments

#### Key Test Methods
- `test_inventory_adjustment_increase()` - Increase adjustment processing
- `test_inventory_adjustment_decrease()` - Decrease adjustment processing
- `test_multiple_adjustments_consistency()` - Multiple adjustment validation
- `test_negative_quantity_prevention()` - Negative quantity prevention
- `test_zero_quantity_adjustment_prevention()` - Zero adjustment prevention

### 5. Order Entry Documents Behavior Tests

#### Test Coverage
- **Sales Orders**: Creation and listing verification
- **Purchase Orders**: Creation and listing verification
- **GRV Processing**: Goods Receipt Voucher and inventory updates
- **Supplier Invoices**: Creation and conversion verification
- **Document Conversions**: SO→Invoice, PO→GRV→Supplier Invoice
- **Status Updates**: Document status tracking throughout processes

#### Key Test Methods
- `test_sales_order_creation_and_listing()` - Sales order processing
- `test_purchase_order_creation_and_listing()` - Purchase order processing
- `test_grv_creation_and_inventory_updates()` - GRV and inventory updates
- `test_supplier_invoice_creation_from_grv()` - Invoice conversion
- `test_complete_purchase_to_pay_cycle()` - Full P2P workflow
- `test_complete_order_to_cash_cycle()` - Full O2C workflow
- `test_document_status_tracking()` - Status progression validation

### Running Transaction Behavior Tests

#### Individual Module Testing
```bash
# Run GL behavior tests
pytest backend/test_transaction_behavior_gl.py -v

# Run AR behavior tests  
pytest backend/test_transaction_behavior_ar.py -v

# Run AP behavior tests
pytest backend/test_transaction_behavior_ap.py -v

# Run Inventory behavior tests
pytest backend/test_transaction_behavior_inventory.py -v

# Run Order Entry behavior tests
pytest backend/test_transaction_behavior_orders.py -v
```

#### All Transaction Behavior Tests
```bash
# Run all transaction behavior tests
pytest backend/test_transaction_behavior_*.py -v

# Run with coverage
pytest backend/test_transaction_behavior_*.py --cov=app --cov-report=html
```

### Test Data Requirements

#### Prerequisites
- Test database with proper schema
- Test user with appropriate permissions
- Sample GL accounts (Assets, Liabilities, Income, Expenses)
- Sample customers and suppliers
- Sample inventory items
- Transaction types configured

#### Validation Points
- **Data Integrity**: All transactions maintain referential integrity
- **Business Rules**: System enforces business validation rules
- **Balance Calculations**: All balances calculate correctly
- **Status Workflows**: Document statuses update appropriately
- **API Consistency**: API endpoints match business logic behavior
- **Error Handling**: System properly handles invalid operations

### Expected Outcomes

#### Success Criteria
- All transaction behaviors work as specified
- Balance calculations are accurate
- Document conversions maintain data integrity
- Status updates reflect business process state
- API endpoints provide consistent behavior
- Error conditions are properly handled

#### Performance Expectations
- Transaction processing completes within reasonable time
- Balance calculations are efficient
- Large document conversions handle appropriately
- API responses maintain acceptable response times

### Integration with Existing Tests

These transaction behavior tests complement the existing CRUD tests by:
- **Validating Business Logic**: Beyond basic CRUD operations
- **Testing Workflows**: Complete business process flows
- **Verifying Calculations**: Financial and inventory calculations
- **Ensuring Consistency**: Data consistency across modules
- **API Validation**: End-to-end API behavior verification
