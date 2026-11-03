
"""finalize canteen schema

Revision ID: 02c00aae5b24
Revises: 43de0016e913
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "02c00aae5b24"
down_revision: Union[str, Sequence[str], None] = "43de0016e913"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "menu_items",
        "price",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="price::integer",
    )

    op.create_check_constraint(
        "ck_menu_items_price_positive",
        "menu_items",
        "price > 0",
    )

    op.alter_column(
        "menu_items",
        "available",
        existing_type=sa.Boolean(),
        server_default=sa.text("true"),
        existing_nullable=False,
    )

    op.drop_column("orders", "customer_name")
    op.drop_column("orders", "total_amount")

    op.drop_index("ix_categories_id", table_name="categories")
    op.drop_index("ix_menu_items_id", table_name="menu_items")
    op.drop_index("ix_orders_id", table_name="orders")


def downgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "customer_name",
            sa.String(150),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "total_amount",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "orders", "customer_name", server_default=None
    )
    op.alter_column(
        "orders", "total_amount", server_default=None
    )

    op.create_index(
        "ix_categories_id", "categories", ["id"], unique=False
    )
    op.create_index(
        "ix_menu_items_id", "menu_items", ["id"], unique=False
    )
    op.create_index(
        "ix_orders_id", "orders", ["id"], unique=False
    )

    op.alter_column(
        "menu_items",
        "available",
        existing_type=sa.Boolean(),
        server_default=None,
        existing_nullable=False,
    )

    op.drop_constraint(
        "ck_menu_items_price_positive",
        "menu_items",
        type_="check",
    )

    op.alter_column(
        "menu_items",
        "price",
        existing_type=sa.Integer(),
        type_=sa.Numeric(10, 2),
        existing_nullable=False,
        postgresql_using="price::numeric(10,2)",
    )
