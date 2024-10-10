# defining database app
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY, func, TEXT, create_engine, MetaData
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
    Column("email", String(128)),
    Column("password", String(255)),
    Column("age", Integer),
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean),
    Column("created_at", Date, server_default=func.now()),
)

positions = Table(
    "positions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(128)),
    Column("price", Integer),
    # Column("tags", ARRAY),
    Column("created_at", Date, server_default=func.now())
)

tokens = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False)
)
