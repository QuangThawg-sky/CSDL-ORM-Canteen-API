
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Category, MenuItem


def seed():
    with SessionLocal() as db:
        categories = {
            "Cơm": [
                ("Cơm gà", "Cơm gà thơm ngon", Decimal("35000.00")),
                ("Cơm sườn", "Cơm sườn nướng", Decimal("40000.00")),
            ],
            "Đồ uống": [
                ("Trà chanh", "Trà chanh mát lạnh", Decimal("15000.00")),
                ("Nước suối", "Nước suối đóng chai", Decimal("10000.00")),
            ],
        }

        for category_name, items in categories.items():
            category = db.scalar(
                select(Category).where(Category.name == category_name)
            )

            if category is None:
                category = Category(name=category_name)
                db.add(category)
                db.flush()

            for name, description, price in items:
                existing = db.scalar(
                    select(MenuItem).where(
                        MenuItem.name == name,
                        MenuItem.category_id == category.id,
                    )
                )

                if existing is None:
                    db.add(
                        MenuItem(
                            name=name,
                            description=description,
                            price=price,
                            category_id=category.id,
                        )
                    )

        db.commit()
        print("Da them du lieu mau thanh cong!")


if __name__ == "__main__":
    seed()
