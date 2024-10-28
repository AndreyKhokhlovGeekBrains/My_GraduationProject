# database operations

from .models import users, newsletter_subscriptions, tokens, products, cards, orders
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
    print(result[0].id)
    if not result:
        print("No featured items found")
        return []  # Return an empty list if no rows are found

    featured_items = []
    for row in result:
        print(row["id"])
        print(row["title"])
        featured_items.append({
            "id": row["id"],
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": f"${row['price']}"
        })

    return featured_items


async def add_item(item_in):
    query = products.insert().values(**item_in.dict())
    return await database.execute(query)


async def get_item_by_id(item_id):
    products_list = None
    query = products.select().where(products.c.id == item_id)
    try:
        products_list = await database.fetch_one(query)
    except Exception as e:
        print(e)
    finally:
        print(products_list)
        return products_list


async def get_items_by_ids(item_ids: list):
    products_list = []
    try:
        # Преобразуем item_ids в кортеж для использования в запросе
        item_ids_tuple = tuple(int(item_id) for item_id in item_ids)

        # Выполняем один запрос для получения всех продуктов с заданными id
        query = products.select().where(products.c.id.in_(item_ids_tuple))
        products_list = await database.fetch_all(query)
    except Exception as e:
        print("get_items: ", e)
    finally:
        print(products_list)
        return products_list


async def create_user(user_in):
    print("Creating user:", user_in)
    try:
        query = users.insert().values(**user_in.dict())
        result = await database.execute(query)
        print(result)
    except Exception as e:
        print(e)


async def update_user_by_id(user_id, **kwargs):
    try:
        query = users.update(**kwargs).where(users.c.id == user_id)
        result = await database.execute(query)
        print(result)
    except Exception as e:
        print(f"Update user: {e}")


async def update_user_by_name(username, **kwargs):
    try:
        query = users.update(**kwargs).where(users.c.name == username)
        result = await database.execute(query)
        print(result)
    except Exception as e:
        print(f"Update user: {e}")


async def get_users(skip: int = 0, limit: int = 10):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_user_by_login_data(email: str):
    query = users.select().where(users.c.email == email)
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def update_user(user_id: int, new_user):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


async def is_user_have_card(user_id: int):
    query = select(cards).where(cards.c.user_id == user_id)
    return await database.fetch_one(query)


async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)


async def add_order_to_db(order_in):
    print("Creating order:", order_in.dict())
    query = orders.insert().values(**order_in.dict())
    return await database.execute(query)


async def find_items_by_name(name: str):
    query = products.select().where(products.c.title.ilike(f"%{name}%"))
    result = await database.fetch_all(query)
    items_by_category = []
    for row in result:
        items_by_category.append({
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": f"${row['price']}"
        })
    return items_by_category


async def add_card(card_in):
    query = cards.insert().values(**card_in.dict())
    await database.execute(query)


async def add_newsletter_mail(newsletter_in):
    query = newsletter_subscriptions.insert().values(**newsletter_in.dict(exclude={"created_at"}))
    await database.execute(query)


async def add_token_to_blacklist(token_in):
    query = tokens.insert().values(**token_in.dict())
    await database.execute(query)


async def get_token(token):
    query = tokens.select().where(positions.c.token == token)
    await database.fetch_one(query)
