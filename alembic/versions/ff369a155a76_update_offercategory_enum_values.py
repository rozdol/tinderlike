"""Update OfferCategory enum values

Revision ID: ff369a155a76
Revises: aa4c9e44358f
Create Date: 2025-08-26 14:36:48.347628

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ff369a155a76'
down_revision = 'aa4c9e44358f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER TYPE for enums, so we'll just update the data
    # The enum values will be handled by the application layer
    op.execute("UPDATE offers SET category = 'ECOMMERCE' WHERE category = 'STOCK_BROKER'")
    op.execute("UPDATE offers SET category = 'OTHER' WHERE category = 'PROPERTY'")


def downgrade() -> None:
    # Revert the changes
    op.execute("UPDATE offers SET category = 'STOCK_BROKER' WHERE category = 'ECOMMERCE'")
    op.execute("UPDATE offers SET category = 'PROPERTY' WHERE category = 'OTHER'")
