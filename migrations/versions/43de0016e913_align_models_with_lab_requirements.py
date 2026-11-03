"""align models with lab requirements

Revision ID: 43de0016e913
Revises: e05b550f9a05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "43de0016e913"
down_revision: Union[str, Sequence[str], None] = "e05b550f9a05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Categories
    op.alter_column(
        "categories",
        "name",
        existing_type=sa.String(length=100),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    # Menu items: retain description and existing prices
    op.add_column(
        "menu_items",
        sa.Column(
            "available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "menu_items",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.alter_column(
        "menu_items",
        "name",
        existing_type=sa.String(length=150),
        type_=sa.String(length=100),
        existing_nullable=False,
    )

    # Orders: preserve old columns while adding student_code
    op.add_column(
        "orders",
        sa.Column("student_code", sa.String(length=10), nullable=True),
    )
    op.execute(
        "UPDATE orders SET student_code = customer_name "
        "WHERE student_code IS NULL"
    )
    op.alter_column(
        "orders",
        "student_code",
        existing_type=sa.String(length=10),
        nullable=False,
    )

    # Order items: rename menu_item_id to item_id and use a composite PK.
    # Existing rows are preserved.
    op.drop_constraint(
        "order_items_menu_item_id_fkey",
        "order_items",
        type_="foreignkey",
    )
    op.alter_column(
        "order_items",
        "menu_item_id",
        new_column_name="item_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "fk_order_items_item_id_menu_items",
        "order_items",
        "menu_items",
        ["item_id"],
        ["id"],
    )

    # Replace the old id primary key with (order_id, item_id).
    op.drop_constraint(
        "order_items_pkey",
        "order_items",
        type_="primary",
    )
    op.drop_column("order_items", "id")
    op.create_primary_key(
        "pk_order_items",
        "order_items",
        ["order_id", "item_id"],
    )

    # Remove server defaults after backfilling existing rows.
    op.alter_column("menu_items", "available", server_default=None)
    op.alter_column("menu_items", "updated_at", server_default=None)


def downgrade() -> None:
    # Restore a generated id primary key for order_items.
    op.drop_constraint("pk_order_items", "order_items", type_="primary")
    op.add_column(
        "order_items",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=True,
        ),
    )
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS order_items_id_seq"
    )
    op.execute(
        "UPDATE order_items SET id = nextval('order_items_id_seq') "
        "WHERE id IS NULL"
    )
    op.alter_column(
        "order_items",
        "id",
        nullable=False,
        server_default=sa.text("nextval('order_items_id_seq')"),
    )
    op.execute(
        "ALTER SEQUENCE order_items_id_seq "
        "OWNED BY order_items.id"
    )
    op.create_primary_key("order_items_pkey", "order_items", ["id"])

    op.drop_constraint(
        "fk_order_items_item_id_menu_items",
        "order_items",
        type_="foreignkey",
    )
    op.alter_column(
        "order_items",
        "item_id",
        new_column_name="menu_item_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "order_items_menu_item_id_fkey",
        "order_items",
        "menu_items",
        ["menu_item_id"],
        ["id"],
    )

    op.drop_column("orders", "student_code")

    op.alter_column(
        "menu_items",
        "name",
        existing_type=sa.String(length=100),
        type_=sa.String(length=150),
        existing_nullable=False,
    )
    op.drop_column("menu_items", "updated_at")
    op.drop_column("menu_items", "available")

    op.alter_column(
        "categories",
        "name",
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
