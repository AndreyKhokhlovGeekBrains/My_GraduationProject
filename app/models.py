# defining database app

from sqlalchemy import (Table, Column, Integer, String, ForeignKey, Numeric, Enum, Boolean, Date,
                        DateTime, ARRAY, func, DECIMAL)
from .db import metadata
from app.schemas import GenderCategory


item_type = Table(
    "item_type",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("description", String(30), nullable=False)
)

# a table where all goods are listed
products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(32)),
    Column("description", String(255)),
    Column("quantity", Integer, nullable=False, default=0),
    Column("price", Numeric(10, 2), nullable=False),  # Numeric for precision
    Column("discount", Numeric(5, 4), nullable=True),  # Numeric for precision
    Column("created_at", DateTime, server_default=func.now()),
    Column("is_featured", String(50), nullable=False),  # Could be changed to Enum
    Column("gender_category", Enum(GenderCategory), nullable=False),
    # Column("item_type", String(50), nullable=False),
    Column("item_type_id", Integer, ForeignKey("item_type.id"), nullable=False),
    Column("image_filename", String(255), nullable=True),  # Add this column to store the image filename
    Column("status", String(50), nullable=False, server_default="Active")
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(32)),
    Column("email", String(128), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean, default=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("status", String(50), nullable=False, server_default="Active")
)

newsletter_subscriptions = Table(
    "newsletter_sbsr",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),  # filled in only if a user signed in
    Column("email", String(128), nullable=False, unique=True),
    Column("created_at", DateTime, server_default=func.now()),
)

tokens = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False, unique=True)
)

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),  # Ensures user is specified
    Column("created_at", DateTime, server_default=func.now(), nullable=False),  # Default creation timestamp
    Column("delivered_at", DateTime, nullable=True),  # Optional delivery timestamp without default
    Column("status", String(50), server_default="Pending", nullable=False),  # Default status set to 'Pending'
    Column("total_amount", DECIMAL(10, 2), nullable=False),
    Column("address", String(255), nullable=False)
)


order_items = Table(
    "order_items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("orders.id"), nullable=False),  # Links to orders table
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False),  # Links to products table
    Column("price", DECIMAL(10, 2), nullable=False),  # Price of the product at the time of the order
    Column("discount", DECIMAL(5,4), nullable=True),
    Column("quantity", Integer, nullable=False)  # Quantity of the product ordered
)

# cards = Table(
#     "cards",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("user_id", Integer, ForeignKey("users.id")),
#     Column("card_owner", String(64), nullable=False, unique=True),
#     Column("card_number", String(20), nullable=False, unique=True),
#     Column("card_exp_date", String(5), nullable=False, unique=True),
#     Column("card_cvv", String(3), nullable=False, unique=True),
#     Column("created_at", DateTime, server_default=func.now()),
#     Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
# )

