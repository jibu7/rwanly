"""merge inventory and ap heads

Revision ID: 3fbb0f49c23a
Revises: 8a76f4c2e014, 2ad5bfa233c0
Create Date: 2025-05-26 02:51:22.879462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fbb0f49c23a'
down_revision = ('8a76f4c2e014', '67964aae7f8f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
