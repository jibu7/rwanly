"""Add AR models

Revision ID: 05918ffb336e
Revises: 61d04a562bec
Create Date: 2025-05-26 01:22:04.249979

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '05918ffb336e'
down_revision = '61d04a562bec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('payment_terms_days', sa.Integer(), nullable=True),
        sa.Column('credit_limit', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('current_balance', sa.DECIMAL(precision=15, scale=2), server_default='0.00', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
    op.create_index(op.f('ix_customers_customer_code'), 'customers', ['customer_code'], unique=False)
    op.create_index('ix_customers_company_customer_code', 'customers', ['company_id', 'customer_code'], unique=True)

    # Create ar_transaction_types table
    op.create_table('ar_transaction_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type_code', sa.String(length=20), nullable=False),
        sa.Column('type_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gl_account_id', sa.Integer(), nullable=False),
        sa.Column('default_income_account_id', sa.Integer(), nullable=True),
        sa.Column('affects_balance', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['gl_account_id'], ['gl_accounts.id'], ),
        sa.ForeignKeyConstraint(['default_income_account_id'], ['gl_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ar_transaction_types_id'), 'ar_transaction_types', ['id'], unique=False)
    op.create_index('ix_ar_transaction_types_company_code', 'ar_transaction_types', ['company_id', 'type_code'], unique=True)

    # Create ar_transactions table
    op.create_table('ar_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type_id', sa.Integer(), nullable=False),
        sa.Column('accounting_period_id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('reference_number', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('gross_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.DECIMAL(precision=15, scale=2), server_default='0.00', nullable=True),
        sa.Column('discount_amount', sa.DECIMAL(precision=15, scale=2), server_default='0.00', nullable=True),
        sa.Column('net_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('outstanding_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('source_module', sa.String(length=50), server_default='AR', nullable=True),
        sa.Column('source_document_id', sa.Integer(), nullable=True),
        sa.Column('is_posted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('posted_by', sa.Integer(), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['accounting_period_id'], ['accounting_periods.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['transaction_type_id'], ['ar_transaction_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ar_transactions_id'), 'ar_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_ar_transactions_reference_number'), 'ar_transactions', ['reference_number'], unique=False)

    # Create ar_allocations table
    op.create_table('ar_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('allocated_to_id', sa.Integer(), nullable=False),
        sa.Column('allocation_date', sa.Date(), nullable=False),
        sa.Column('allocated_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('posted_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['allocated_to_id'], ['ar_transactions.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['ar_transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ar_allocations_id'), 'ar_allocations', ['id'], unique=False)

    # Create ageing_periods table
    op.create_table('ageing_periods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('period_name', sa.String(length=50), nullable=False),
        sa.Column('days_from', sa.Integer(), nullable=False),
        sa.Column('days_to', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ageing_periods_id'), 'ageing_periods', ['id'], unique=False)
    op.create_index('ix_ageing_periods_company_sort', 'ageing_periods', ['company_id', 'sort_order'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_ageing_periods_company_sort', table_name='ageing_periods')
    op.drop_index(op.f('ix_ageing_periods_id'), table_name='ageing_periods')
    op.drop_table('ageing_periods')
    op.drop_index(op.f('ix_ar_allocations_id'), table_name='ar_allocations')
    op.drop_table('ar_allocations')
    op.drop_index(op.f('ix_ar_transactions_reference_number'), table_name='ar_transactions')
    op.drop_index(op.f('ix_ar_transactions_id'), table_name='ar_transactions')
    op.drop_table('ar_transactions')
    op.drop_index('ix_ar_transaction_types_company_code', table_name='ar_transaction_types')
    op.drop_index(op.f('ix_ar_transaction_types_id'), table_name='ar_transaction_types')
    op.drop_table('ar_transaction_types')
    op.drop_index('ix_customers_company_customer_code', table_name='customers')
    op.drop_index(op.f('ix_customers_customer_code'), table_name='customers')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
