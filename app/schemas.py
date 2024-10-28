from pydantic import BaseModel, Field, EmailStr, constr
from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Optional
from decimal import Decimal


class GenderCategory(PyEnum):
    man = "man"
    women = "women"
    kids = "kids"


class ItemIn(BaseModel):
    title: constr(max_length=32) = Field(..., description="Title of the item")
    description: constr(max_length=255) = Field(..., description="Description of the item")
    price: float = Field(..., description="Item price")
    discount: Optional[float] = None
    is_featured: constr(max_length=50) = Field(..., description="This indicates whether an item is featured or not")
    gender_category: GenderCategory = Field(..., description="Specifies a gender category")
    item_type: constr(max_length=50) = Field(..., description="Specifies a category: Accessories, Polos etc")
    image_filename: constr(max_length=100) = Field(..., description="Specifies a file attributed to the record")


class UserIn(BaseModel):
    name: constr(max_length=32) = Field(..., description="Name of the user")
    email: constr(max_length=128) = Field(..., description="Email of the user")
    password: constr(min_length=8, max_length=255) = Field(..., description="Password with minimum 8 characters")
    birthdate: date = Field(..., description="Birthdate in YYYY-MM-DD format")
    phone: str = Field(..., pattern=r'^\+?\d{7,20}$', description="Phone number with 7-20 digits")
    agreement: bool = Field(..., description="User  agreement checkbox")


class NewsletterIn(BaseModel):
    email: EmailStr = Field(..., description="Newsletter email")


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


class Statuses(PyEnum):
    placing = "placing"
    delivery = "delivery"
    delivered = "delivered"


class OrderIn(BaseModel):
    user_id: int
    item_id: int
    amount: int
    address: str
    price: Decimal
    status: str


class CardIn(BaseModel):
    user_id: int
    card_owner: str
    card_number: str
    card_exp_date: str
    card_cvv: str


class TokenIn(BaseModel):
    token: str = Field(None, description="Token")


class Token(BaseModel):
    id: int
    token: str
