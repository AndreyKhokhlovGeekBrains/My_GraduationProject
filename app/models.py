# defining database app
# models.py

from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY, func
from .db import metadata
from datetime import datetime

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

