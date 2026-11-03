
"""add updated_at server default"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "174e19ba1306"
down_revision: Union[str, Sequence[str], None] = "02c00aae5b24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "menu_items",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "menu_items",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False,
    )
