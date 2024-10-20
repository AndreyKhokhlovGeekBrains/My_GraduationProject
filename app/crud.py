# database operations
from .models import users, newsletter_subscriptions, positions, tokens, products
from .db import database
from sqlalchemy import select
from typing import Optional


async def get_all_items():
    query = select(products)
    result = await database.fetch_all(query)
    all_items = []
    for row in result:
        all_items.append({
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": f"${row['price']}"
        })

    return all_items


async def get_items_by_category(gender: str, item_type: Optional[str] = None):
    query = select(products).where(products.c.gender_category == gender)

    if item_type:
        query = select(products).where(products.c.gender_category == gender, products.c.item_type == item_type)

    result = await database.fetch_all(query)

    if not result:
        print(f"No items found for {gender} - {item_type}")

    items_by_category = []
    for row in result:
        items_by_category.append({
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": f"${row['price']}"
        })
    return items_by_category


async def load_featured_items():
    query = select(products).where(products.c.is_featured == 'featured')
    result = await database.fetch_all(query)

    if not result:
        print("No featured items found")
        return []  # Return an empty list if no rows are found

    featured_items = []
    for row in result:
        featured_items.append({
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": f"${row['price']}"
        })

    return featured_items


async def add_item(item_in):
    query = products.insert().values(**item_in.dict())
    return await database.execute(query)


async def create_user(user_in):
    print("Creating user:", user_in)
    try:
        query = users.insert().values(**user_in.dict())
        result = await database.execute(query)
        logging.info(f"User  created: {result}")
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise

async def get_users(skip: int = 0, limit: int = 10):
    query = User.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_user_by_login_data(email: str, password: str):
    query = User.select().where(User.email == email).where(User.hashed_password == password)
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    query = User.select().where(User.id == user_id)
    return await database.fetch_one(query)


async def update_user(user_id: int, new_user):
    query = User.update().where(User.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


async def delete_user(user_id: int):
    query = User.delete().where(User.id == user_id)
    await database.execute(query)


async def add_newsletter_mail(newsletter_in):
    query = newsletter_subscriptions.insert().values(**newsletter_in.dict(exclude={"created_at"}))
    await database.execute(query)


async def create_position(position_in):
    query = Car.insert().values(**position_in.dict())
    await database.execute(query)


async def get_positions(skip: int = 0, limit: int = 10):
    query = positions.select().offset(skip).limit(limit)
    return await Car.fetch_all(query)


async def get_position_by_id(position_id: int):
    query = positions.select().where(positions.c.id == position_id)
    return await database.fetch_one(query)


async def add_token_to_blacklist(token_in):
    query = Token.insert().values(**token_in.dict())
    await database.execute(query)


async def get_token(token):
    query = tokens.select().where(positions.c.token == token)
    await database.fetch_one(query)
