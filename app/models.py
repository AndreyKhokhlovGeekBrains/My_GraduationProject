# defining database app
<<<<<<< HEAD
# models.py

from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY, func
from .db import metadata
=======
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY, func, TEXT, create_engine, MetaData
>>>>>>> ea4a09d2c20a4d9611a5515123ba27b2c23e7a21
from datetime import datetime


from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


# database_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
database_url = "sqlite:///mydatabase.db"
engine = create_engine(url=database_url)
# engine = create_async_engine(url=database_url)
# async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
metadata = MetaData()
"""
class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Added name field
    age: Mapped[int] = mapped_column(Integer)
    birthdate: Mapped[datetime] = mapped_column(Date)
    phone: Mapped[str] = mapped_column(String)  # Added phone field
    agreement: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Car(Base):
    __tablename__ = "cars"

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(TEXT, nullable=False)

class Token(Base):
    __tablename__ = "tokens"

    token: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
"""

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(32)),
<<<<<<< HEAD
    Column("email", String(128), nullable=False),
    Column("password", String(255), nullable=False),
=======
    Column("email", String(128)),
    Column("password", String(255)),
    Column("age", Integer),
>>>>>>> ea4a09d2c20a4d9611a5515123ba27b2c23e7a21
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean, default=False),
    Column("created_at", DateTime, server_default=func.now()),
)

positions = Table(
    "positions",
    metadata,
    Column("id", Integer, primary_key=True),
<<<<<<< HEAD
    Column("name", String(128), nullable=False),
    Column("price", Integer, nullable=False),
    Column("tags", ARRAY(String)),  # Use ARRAY or JSON for multiple tags
    Column("created_at", DateTime, server_default=func.now())
=======
    Column("name", String(128)),
    Column("price", Integer),
    # Column("tags", ARRAY),
    Column("created_at", Date, server_default=func.now())
>>>>>>> ea4a09d2c20a4d9611a5515123ba27b2c23e7a21
)

tokens = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False, unique=True)
)

