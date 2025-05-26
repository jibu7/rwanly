"""add_inventory_models

Revision ID: 8a76f4c2e014
Revises: 67964aae7f8f
Create Date: 2025-05-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a76f4c2e014'
down_revision = '67964aae7f8f'
branch_labels = None
depends_on = None


def upgrade():
    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('item_code', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=False),
        sa.Column('cost_price', sa.DECIMAL(precision=15, scale=2), default=0.00),
        sa.Column('selling_price', sa.DECIMAL(precision=15, scale=2), default=0.00),
        sa.Column('quantity_on_hand', sa.DECIMAL(precision=15, scale=2), default=0.00),
        sa.Column('costing_method', sa.String(length=20), default='WEIGHTED_AVERAGE'),
        sa.Column('gl_asset_account_id', sa.Integer(), nullable=False),
        sa.Column('gl_expense_account_id', sa.Integer(), nullable=False),
        sa.Column('gl_revenue_account_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['gl_asset_account_id'], ['gl_accounts.id']),
        sa.ForeignKeyConstraint(['gl_expense_account_id'], ['gl_accounts.id']),
        sa.ForeignKeyConstraint(['gl_revenue_account_id'], ['gl_accounts.id'])
    )
    op.create_index('ix_inventory_items_item_code', 'inventory_items', ['item_code'])

    # Create inventory_transaction_types table
    op.create_table(
        'inventory_transaction_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type_code', sa.String(length=20), nullable=False),
        sa.Column('type_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('affects_quantity', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'])
    )

    # Create inventory_transactions table
    op.create_table(
        'inventory_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type_id', sa.Integer(), nullable=False),
        sa.Column('accounting_period_id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('reference_number', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('unit_cost', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('total_cost', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('source_module', sa.String(length=50)),
        sa.Column('source_document_id', sa.Integer()),
        sa.Column('is_posted', sa.Boolean(), default=False),
        sa.Column('posted_by', sa.Integer()),
        sa.Column('posted_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id']),
        sa.ForeignKeyConstraint(['transaction_type_id'], ['inventory_transaction_types.id']),
        sa.ForeignKeyConstraint(['accounting_period_id'], ['accounting_periods.id']),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id'])
    )
    op.create_index('ix_inventory_transactions_reference_number', 'inventory_transactions', ['reference_number'])


def downgrade():
    op.drop_table('inventory_transactions')
    op.drop_table('inventory_transaction_types')
    op.drop_table('inventory_items')
