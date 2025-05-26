import sys
from datetime import date
from decimal import Decimal
sys.path.append('.')

from app.database.database import SessionLocal
from app.models.core import Company, Supplier, APTransactionType, AccountingPeriod
from app.crud.accounts_payable import ap_transaction_crud, ap_transaction_type_crud, supplier_crud
from app.schemas.core import APTransactionCreate, APTransactionUpdate, APTransactionTypeCreate, SupplierCreate

print('Testing AP Transaction Type and Transaction CRUD...')
db = SessionLocal()
print('Database session created.')

def get_or_create_supplier(db, company):
    supplier = db.query(Supplier).filter(Supplier.company_id == company.id).first()
    if not supplier:
        supplier_data = SupplierCreate(
            company_id=company.id,
            supplier_code='SUP-001',
            name='Test Supplier',
            contact_person='Test Person',
            email='supplier@example.com',
            phone='1234567890',
            address_line1='123 Test St',
            city='Testville',
            state='TestState',
            postal_code='12345',
            country='Testland',
            payment_terms_days=30,
            credit_limit=Decimal('10000.00'),
            is_active=True
        )
        supplier = supplier_crud.create_supplier(db, supplier_data)
    return supplier

def get_or_create_period(db, company):
    period = db.query(AccountingPeriod).filter(AccountingPeriod.company_id == company.id).first()
    return period

def get_first_gl_account(db, company, account_type, code_like):
    from app.models.core import GLAccount
    return db.query(GLAccount).filter(
        GLAccount.company_id == company.id,
        GLAccount.account_type == account_type,
        GLAccount.account_code.like(code_like)
    ).first()

def get_or_create_ap_type(db, company, type_code, gl_account_id, default_expense_account_id, affects_balance):
    ap_type = db.query(APTransactionType).filter(
        APTransactionType.company_id == company.id,
        APTransactionType.type_code == type_code
    ).first()
    if not ap_type:
        ap_type_data = APTransactionTypeCreate(
            company_id=company.id,
            type_code=type_code,
            type_name=f'Test {type_code}',
            description=f'Test {type_code} type',
            gl_account_id=gl_account_id,
            default_expense_account_id=default_expense_account_id,
            affects_balance=affects_balance,
            is_active=True
        )
        ap_type = ap_transaction_type_crud.create_transaction_type(db, ap_type_data)
    return ap_type

try:
    company = db.query(Company).first()
    assert company, 'No company found.'
    supplier = get_or_create_supplier(db, company)
    assert supplier, 'No supplier found.'
    period = get_or_create_period(db, company)
    assert period, 'No accounting period found.'
    ap_control_account = get_first_gl_account(db, company, 'Liabilities', '21%')
    expense_account = get_first_gl_account(db, company, 'Expenses', '50%')
    assert ap_control_account, 'No AP control account found.'
    assert expense_account, 'No expense account found.'

    # --- AP Transaction Type CRUD ---
    print('Testing APTransactionType creation...')
    new_type_code = 'TST-AP'
    ap_type = get_or_create_ap_type(db, company, new_type_code, ap_control_account.id, expense_account.id, 'CREDIT')
    print(f'Created APTransactionType: {ap_type.type_code} (ID: {ap_type.id})')

    print('Testing APTransactionType get by ID...')
    fetched_type = ap_transaction_type_crud.get_transaction_type(db, ap_type.id, company.id)
    assert fetched_type is not None and fetched_type.type_code == new_type_code

    print('Testing APTransactionType update...')
    from app.schemas.core import APTransactionTypeUpdate
    update_data = APTransactionTypeUpdate(type_name='Updated AP Type', description='Updated desc')
    updated_type = ap_transaction_type_crud.update_transaction_type(db, ap_type.id, company.id, update_data)
    assert updated_type.type_name == 'Updated AP Type'

    print('Testing APTransactionType list...')
    all_types = ap_transaction_type_crud.get_transaction_types(db, company.id)
    assert any(t.id == ap_type.id for t in all_types)

    # --- AP Transaction CRUD ---
    print('Testing APTransaction creation (Invoice)...')
    invoice_type = get_or_create_ap_type(db, company, 'PINV', ap_control_account.id, expense_account.id, 'CREDIT')
    invoice_data = APTransactionCreate(
        company_id=company.id,
        supplier_id=supplier.id,
        transaction_type_id=invoice_type.id,
        accounting_period_id=period.id,
        transaction_date=date.today(),
        due_date=date.today(),
        reference_number='PINV-TEST-001',
        description='Test supplier invoice',
        gross_amount=Decimal('2000.00'),
        tax_amount=Decimal('200.00'),
        discount_amount=Decimal('0.00'),
        source_module='AP',
        source_document_id=None
    )
    invoice = ap_transaction_crud.create_transaction(db, invoice_data)
    print(f'Created APTransaction (Invoice): {invoice.reference_number} (ID: {invoice.id})')
    assert invoice.net_amount == Decimal('2200.00')
    assert invoice.outstanding_amount == Decimal('2200.00')

    print('Testing APTransaction get by ID...')
    fetched_invoice = ap_transaction_crud.get_transaction(db, invoice.id, company.id)
    assert fetched_invoice is not None and fetched_invoice.reference_number == 'PINV-TEST-001'

    print('Testing APTransaction update (before posting)...')
    update_data = APTransactionUpdate(description='Updated supplier invoice', gross_amount=Decimal('2500.00'))
    updated_invoice = ap_transaction_crud.update_transaction(db, invoice.id, company.id, update_data)
    assert updated_invoice.description == 'Updated supplier invoice'
    assert updated_invoice.gross_amount == Decimal('2500.00')
    assert updated_invoice.net_amount == Decimal('2700.00')

    print('Testing APTransaction list...')
    all_transactions = ap_transaction_crud.get_transactions(db, company.id)
    assert any(t.id == invoice.id for t in all_transactions)

    print('Testing APTransaction posting...')
    from app.models.core import User
    admin_user = db.query(User).filter(User.username == 'admin').first() or db.query(User).first()
    posted_invoice = ap_transaction_crud.post_transaction(db, invoice.id, company.id, admin_user.id)
    assert posted_invoice.is_posted is True
    assert posted_invoice.posted_by == admin_user.id
    assert posted_invoice.posted_at is not None

    print('Testing APTransaction update after posting (should fail)...')
    try:
        ap_transaction_crud.update_transaction(db, invoice.id, company.id, APTransactionUpdate(description='Should fail'))
        print('ERROR: Update after posting did not fail as expected!')
    except Exception as e:
        print(f'Expected error on update after posting: {e}')

    print('Testing APTransaction posting again (should fail)...')
    try:
        ap_transaction_crud.post_transaction(db, invoice.id, company.id, admin_user.id)
        print('ERROR: Posting already posted transaction did not fail as expected!')
    except Exception as e:
        print(f'Expected error on double posting: {e}')

    print('Testing outstanding supplier invoices...')
    outstanding = ap_transaction_crud.get_outstanding_invoices(db, company.id, supplier.id)
    print(f'Outstanding invoices for supplier: {[t.reference_number for t in outstanding]}')

    print('AP Transaction Type and Transaction CRUD tests completed successfully!')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
    print('Database session closed.')
print("Script finished")
