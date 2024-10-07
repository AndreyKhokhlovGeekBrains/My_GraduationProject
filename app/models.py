# defining database app
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY, func
from .db import metadata
from sqlalchemy.sql import func
from datetime import datetime

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(32)),
    Column("email", String(128)),
    Column("password", String(255)),
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean),
    Column("created_at", Date, server_default=func.now),
)

positions = Table(
    "positions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(128)),
    Column("price", Integer),
    Column("tags", ARRAY),
    Column("created_at", Date, server_default=func.now())
)

tokens = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False)
)
