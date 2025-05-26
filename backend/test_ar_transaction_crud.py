import sys
print("Script started") # Basic print to check execution
sys.path.append('.')

from app.database.database import SessionLocal
from app.models.core import Company, Customer, ARTransactionType, AccountingPeriod
from app.crud.accounts_receivable import ar_transaction_crud
from app.schemas.core import ARTransactionCreate
from datetime import date
from decimal import Decimal


print('Testing AR Transaction Type and Transaction CRUD...')
db = SessionLocal()
print('Database session created.')

def get_or_create_admin_user(db):
    from app.models.core import User
    user = db.query(User).filter(User.username == 'admin').first()
    if not user:
        user = db.query(User).first()
    return user

def get_or_create_period(db, company):
    from app.models.core import AccountingPeriod
    period = db.query(AccountingPeriod).filter(AccountingPeriod.company_id == company.id).first()
    if not period:
        from app.schemas.core import AccountingPeriodCreate
        from datetime import date
        period_data = AccountingPeriodCreate(
            company_id=company.id,
            period_name='Test Period',
            start_date=date(date.today().year, 1, 1),
            end_date=date(date.today().year, 12, 31),
            status='Open'
        )
        from app.crud.core import accounting_period_crud
        period = accounting_period_crud.create_accounting_period(db, period_data)
    return period

def get_or_create_ar_type(db, company, type_code, gl_account_id, default_income_account_id, affects_balance):
    ar_type = db.query(ARTransactionType).filter(
        ARTransactionType.company_id == company.id,
        ARTransactionType.type_code == type_code
    ).first()
    if not ar_type:
        from app.schemas.core import ARTransactionTypeCreate
        ar_type_data = ARTransactionTypeCreate(
            company_id=company.id,
            type_code=type_code,
            type_name=f'Test {type_code}',
            description=f'Test {type_code} type',
            gl_account_id=gl_account_id,
            default_income_account_id=default_income_account_id,
            affects_balance=affects_balance,
            is_active=True
        )
        from app.crud.accounts_receivable import ar_transaction_type_crud
        ar_type = ar_transaction_type_crud.create_transaction_type(db, ar_type_data)
    return ar_type

def get_first_gl_account(db, company, account_type, code_like):
    from app.models.core import GLAccount
    return db.query(GLAccount).filter(
        GLAccount.company_id == company.id,
        GLAccount.account_type == account_type,
        GLAccount.account_code.like(code_like)
    ).first()

try:
    # Setup: Get or create required data
    company = db.query(Company).first()
    assert company, 'No company found.'
    customer = db.query(Customer).filter(Customer.company_id == company.id).first()
    assert customer, 'No customer found.'
    admin_user = get_or_create_admin_user(db)
    assert admin_user, 'No admin user found.'
    period = get_or_create_period(db, company)
    assert period, 'No accounting period found.'
    ar_control_account = get_first_gl_account(db, company, 'Asset', '12%')
    sales_income_account = get_first_gl_account(db, company, 'Revenue', '40%')
    assert ar_control_account, 'No AR control account found.'
    assert sales_income_account, 'No sales income account found.'

    # --- AR Transaction Type CRUD ---
    from app.crud.accounts_receivable import ar_transaction_type_crud
    from app.schemas.core import ARTransactionTypeCreate, ARTransactionTypeUpdate

    print('Testing ARTransactionType creation...')
    new_type_code = 'TST'
    ar_type = get_or_create_ar_type(db, company, new_type_code, ar_control_account.id, sales_income_account.id, 'DEBIT')
    print(f'Created ARTransactionType: {ar_type.type_code} (ID: {ar_type.id})')

    print('Testing ARTransactionType get by ID...')
    fetched_type = ar_transaction_type_crud.get_transaction_type(db, ar_type.id, company.id)
    assert fetched_type is not None and fetched_type.type_code == new_type_code

    print('Testing ARTransactionType get by code...')
    fetched_by_code = ar_transaction_type_crud.get_transaction_type_by_code(db, new_type_code, company.id)
    assert fetched_by_code is not None and fetched_by_code.id == ar_type.id

    print('Testing ARTransactionType update...')
    update_data = ARTransactionTypeUpdate(type_name='Updated Test Type', description='Updated desc')
    updated_type = ar_transaction_type_crud.update_transaction_type(db, ar_type.id, company.id, update_data)
    assert updated_type.type_name == 'Updated Test Type'

    print('Testing ARTransactionType list...')
    all_types = ar_transaction_type_crud.get_transaction_types(db, company.id)
    assert any(t.id == ar_type.id for t in all_types)

    # --- AR Transaction CRUD ---
    from app.schemas.core import ARTransactionCreate, ARTransactionUpdate
    from app.crud.accounts_receivable import ar_transaction_crud
    from datetime import date
    from decimal import Decimal

    print('Testing ARTransaction creation (Invoice)...')
    invoice_type = get_or_create_ar_type(db, company, 'INV', ar_control_account.id, sales_income_account.id, 'DEBIT')
    invoice_data = ARTransactionCreate(
        company_id=company.id,
        customer_id=customer.id,
        transaction_type_id=invoice_type.id,
        accounting_period_id=period.id,
        transaction_date=date.today(),
        due_date=date.today(),
        reference_number='INV-TEST-001',
        description='Test invoice transaction',
        gross_amount=Decimal('1000.00'),
        tax_amount=Decimal('100.00'),
        discount_amount=Decimal('0.00'),
        source_module='AR',
        source_document_id=None
    )
    invoice = ar_transaction_crud.create_transaction(db, invoice_data)
    print(f'Created ARTransaction (Invoice): {invoice.reference_number} (ID: {invoice.id})')
    assert invoice.net_amount == Decimal('1100.00')
    assert invoice.outstanding_amount == Decimal('1100.00')

    print('Testing ARTransaction get by ID...')
    fetched_invoice = ar_transaction_crud.get_transaction(db, invoice.id, company.id)
    assert fetched_invoice is not None and fetched_invoice.reference_number == 'INV-TEST-001'

    print('Testing ARTransaction update (before posting)...')
    update_data = ARTransactionUpdate(description='Updated invoice desc', gross_amount=Decimal('1200.00'))
    updated_invoice = ar_transaction_crud.update_transaction(db, invoice.id, company.id, update_data)
    assert updated_invoice.description == 'Updated invoice desc'
    assert updated_invoice.gross_amount == Decimal('1200.00')
    assert updated_invoice.net_amount == Decimal('1300.00')

    print('Testing ARTransaction list...')
    all_transactions = ar_transaction_crud.get_transactions(db, company.id)
    assert any(t.id == invoice.id for t in all_transactions)

    print('Testing ARTransaction posting...')
    posted_invoice = ar_transaction_crud.post_transaction(db, invoice.id, company.id, admin_user.id)
    assert posted_invoice.is_posted is True
    assert posted_invoice.posted_by == admin_user.id
    assert posted_invoice.posted_at is not None

    print('Testing ARTransaction update after posting (should fail)...')
    try:
        ar_transaction_crud.update_transaction(db, invoice.id, company.id, ARTransactionUpdate(description='Should fail'))
        print('ERROR: Update after posting did not fail as expected!')
    except Exception as e:
        print(f'Expected error on update after posting: {e}')

    print('Testing ARTransaction posting again (should fail)...')
    try:
        ar_transaction_crud.post_transaction(db, invoice.id, company.id, admin_user.id)
        print('ERROR: Posting already posted transaction did not fail as expected!')
    except Exception as e:
        print(f'Expected error on double posting: {e}')

    print('Testing outstanding invoices...')
    outstanding = ar_transaction_crud.get_outstanding_invoices(db, company.id, customer.id)
    print(f'Outstanding invoices for customer: {[t.reference_number for t in outstanding]}')

    print('AR Transaction Type and Transaction CRUD tests completed successfully!')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    print('Inside finally block.')
    db.close()
    print('Database session closed.')
print("Script finished") # Basic print to check execution
