# defining database app
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime
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
    Column("created_at", Date, server_default=func.now()),  # Use server_default with func.now()
)
