# Pydantic app
from pydantic import BaseModel, Field, constr
from datetime import date, datetime


class UserIn(BaseModel):
    name: constr(max_length=32) = Field(..., description="Name of the user")
    email: constr(max_length=128) = Field(..., description="Email of the user")
    password: constr(min_length=8, max_length=255) = Field(..., description="Password with minimum 8 characters")
    birthdate: date = Field(..., description="Birthdate in YYYY-MM-DD format")
    phone: str = Field(..., pattern=r'^\+?\d{7,20}$', description="Phone number with 7-20 digits")
    agreement: bool = Field(None, description="Check box")
    # created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation date")


class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
