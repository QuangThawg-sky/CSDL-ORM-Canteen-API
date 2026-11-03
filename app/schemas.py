
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# =========================
# DANH MỤC
# =========================

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# =========================
# MÓN ĂN
# =========================

class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    price: int = Field(gt=0)
    category_id: int
    available: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None
    price: int | None = Field(default=None, gt=0)
    category_id: int | None = None
    available: bool | None = None


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: int
    available: bool
    category_id: int
    updated_at: datetime


# =========================
# ĐƠN HÀNG
# =========================

class OrderLineCreate(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    student_code: str = Field(min_length=1, max_length=10)
    lines: list[OrderLineCreate] = Field(min_length=1)


class OrderLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_code: str
    created_at: datetime
    lines: list[OrderLineOut]
    total: Decimal
