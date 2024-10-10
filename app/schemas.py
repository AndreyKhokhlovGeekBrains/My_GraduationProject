# Pydantic app
from pydantic import BaseModel, Field, constr
from datetime import date, datetime


class UserIn(BaseModel):
    name: constr(max_length=32) = Field(..., description="Name of the user")
    email: constr(max_length=128) = Field(..., description="Email of the user")
    hashed_password: constr(min_length=8, max_length=255) = Field(..., description="Password with minimum 8 characters")
    age: int = Field(None, gt=0, description="Age must be a positive integer")  # Age should be greater than 0
    birthdate: date = Field(..., description="Birthdate in YYYY-MM-DD format")
    phone: str = Field(..., pattern=r'^\+?\d{7,20}$', description="Phone number with 7-20 digits")
    agreement: bool = Field(None, description="Check box")


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


class PositionIn(BaseModel):
    name: constr(max_length=128) = Field(..., description="Name of the position")
    price: int = Field(None, gt=0, description="Price of the position")
    tags: list[str] = Field(None, description="Tags")

class Position(BaseModel):
    id: int
    name: str
    price: str
    tags: list[str]
    created_at: datetime


class TokenIn(BaseModel):
    token: str = Field(None, description="Token")


class Token(BaseModel):
    id: int
    token: str
