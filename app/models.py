from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY, func, TEXT, create_engine, MetaData
# defining database app

from sqlalchemy import Table, Column, Integer, String, Float, Numeric, Enum, Boolean, Date, DateTime, ARRAY, func
from .db import metadata
from app.schemas import GenderCategory
from datetime import datetime


# a table where all goods are listed
products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(32)),
    Column("description", String(255)),
    Column("price", Numeric(10, 2), nullable=False),  # Numeric for precision
    Column("discount", Numeric(5, 4), nullable=True),  # Numeric for precision
    Column("created_at", DateTime, server_default=func.now()),
    Column("is_featured", String(50), nullable=False),  # Could be changed to Enum
    Column("gender_category", Enum(GenderCategory), nullable=False),
    Column("item_type", String(50), nullable=False),  # Could be changed to Enum
    Column("image_filename", String(255), nullable=True)  # Add this column to store the image filename
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(32)),
    Column("email", String(128), nullable=False),
    Column("password", String(255), nullable=False),
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean, default=False),
    Column("created_at", DateTime, server_default=func.now()),
)

newsletter_subscriptions = Table(
    "newsletter_sbsr",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=True), # filled in only if a user signed in
    Column("email", String(128), nullable=False, unique=True),
    Column("created_at", DateTime, server_default=func.now()),
)

positions = Table(
    "positions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(128), nullable=False),
    Column("price", Integer, nullable=False),
    Column("tags", ARRAY(String)),  # Use ARRAY or JSON for multiple tags
    Column("created_at", DateTime, server_default=func.now())
)

tokens = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False, unique=True)
)

