
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Category, MenuItem, Order, OrderItem
from app.schemas import (
    CategoryCreate,
    CategoryOut,
    MenuItemCreate,
    MenuItemOut,
    MenuItemUpdate,
    OrderCreate,
    OrderOut,
)

app = FastAPI(title="Canteen API")

DbSession = Annotated[Session, Depends(get_db)]


@app.get("/")
def home():
    return {"message": "Canteen API is running"}


# -------------------- CATEGORIES --------------------

@app.get("/categories", response_model=list[CategoryOut])
def get_categories(db: DbSession):
    return db.scalars(select(Category).order_by(Category.id)).all()


@app.post(
    "/categories",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_category(data: CategoryCreate, db: DbSession):
    name = data.name.strip()

    if not name:
        raise HTTPException(422, "Tên danh mục không được để trống")

    existing = db.scalar(select(Category).where(Category.name == name))
    if existing:
        raise HTTPException(409, "Danh mục đã tồn tại")

    category = Category(name=name)
    db.add(category)

    try:
        db.commit()
        db.refresh(category)
    except Exception:
        db.rollback()
        raise HTTPException(409, "Không thể tạo danh mục")

    return category


# -------------------- MENU ITEMS --------------------

@app.get("/menu-items", response_model=list[MenuItemOut])
def get_menu_items(
    db: DbSession,
    category_id: int | None = None,
    sort: str = Query(default="id"),
    order: str = Query(default="asc"),
):
    allowed_sorts = {
        "id": MenuItem.id,
        "name": MenuItem.name,
        "price": MenuItem.price,
        "updated_at": MenuItem.updated_at,
    }

    if sort not in allowed_sorts:
        raise HTTPException(400, "Trường sắp xếp không hợp lệ")

    if order not in {"asc", "desc"}:
        raise HTTPException(400, "Thứ tự phải là asc hoặc desc")

    stmt = select(MenuItem)

    if category_id is not None:
        stmt = stmt.where(MenuItem.category_id == category_id)

    column = allowed_sorts[sort]
    stmt = stmt.order_by(
        column.asc() if order == "asc" else column.desc()
    )

    return db.scalars(stmt).all()


@app.get("/menu-items/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int, db: DbSession):
    item = db.get(MenuItem, item_id)

    if item is None:
        raise HTTPException(404, "Không tìm thấy món ăn")

    return item


@app.post(
    "/menu-items",
    response_model=MenuItemOut,
    status_code=status.HTTP_201_CREATED,
)
def create_menu_item(data: MenuItemCreate, db: DbSession):
    if db.get(Category, data.category_id) is None:
        raise HTTPException(400, "Danh mục không tồn tại")

    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@app.put("/menu-items/{item_id}", response_model=MenuItemOut)
def update_menu_item(item_id: int, data: MenuItemUpdate, db: DbSession):
    item = db.get(MenuItem, item_id)

    if item is None:
        raise HTTPException(404, "Không tìm thấy món ăn")

    values = data.model_dump(exclude_unset=True)

    if "category_id" in values:
        if db.get(Category, values["category_id"]) is None:
            raise HTTPException(400, "Danh mục không tồn tại")

    for key, value in values.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


@app.patch("/menu-items/{item_id}", response_model=MenuItemOut)
def patch_menu_item(item_id: int, data: MenuItemUpdate, db: DbSession):
    return update_menu_item(item_id, data, db)


@app.delete("/menu-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(item_id: int, db: DbSession):
    item = db.get(MenuItem, item_id)

    if item is None:
        raise HTTPException(404, "Không tìm thấy món ăn")

    ordered = db.scalar(
        select(OrderItem).where(OrderItem.item_id == item_id).limit(1)
    )

    if ordered:
        raise HTTPException(
            409,
            "Món ăn đã có trong đơn hàng; hãy chuyển sang không còn bán",
        )

    db.delete(item)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -------------------- ORDERS --------------------

@app.post(
    "/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_order(data: OrderCreate, db: DbSession):
    item_ids = [line.item_id for line in data.lines]

    if len(item_ids) != len(set(item_ids)):
        raise HTTPException(
            400,
            "Mỗi món ăn chỉ được xuất hiện một lần trong đơn hàng",
        )

    items = {}
    for line in data.lines:
        item = db.get(MenuItem, line.item_id)

        if item is None:
            raise HTTPException(
                404,
                f"Không tìm thấy món ăn ID {line.item_id}",
            )

        if not item.available:
            raise HTTPException(
                409,
                f"Món ăn ID {line.item_id} hiện không còn bán",
            )

        items[line.item_id] = item

    order = Order(student_code=data.student_code.strip())

    for line in data.lines:
        item = items[line.item_id]
        order.lines.append(
            OrderItem(
                item_id=item.id,
                quantity=line.quantity,
                unit_price=item.price,
            )
        )

    db.add(order)
    db.commit()

    saved_order = db.scalar(
        select(Order)
        .options(selectinload(Order.lines))
        .where(Order.id == order.id)
    )

    return saved_order


@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: DbSession):
    order = db.scalar(
        select(Order)
        .options(selectinload(Order.lines))
        .where(Order.id == order_id)
    )

    if order is None:
        raise HTTPException(404, "Không tìm thấy đơn hàng")

    return order
