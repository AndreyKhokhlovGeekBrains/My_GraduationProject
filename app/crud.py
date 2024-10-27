# database operations
from .models import users, newsletter_subscriptions, positions, tokens, products, item_type
from .db import database
from sqlalchemy import select, insert
from typing import Optional
from app.schemas import GenderCategory
from decimal import Decimal

predefined_item_types = [
    "Accessories",
    "Bags",
    "Denim",
    "Jackets & Coats",
    "Polos",
    "T-Shirts",
    "Shirts",
    "Trousers",
    "Shoes"
]


async def populate_item_types():
    # Check if the table is already populated to avoid duplicates
    query = select(item_type.c.description)
    existing_item_types = await database.fetch_all(query)  # A list of dictionaries

    # Convert the list of existing descriptions to a simple list for easy comparison
    existing_item_types_list = [item['description'] for item in existing_item_types]

    # Filter only the new item types that are not already in the database
    new_item_types = [
        {"description": item_type_in} for item_type_in in predefined_item_types
        if item_type_in not in existing_item_types_list
    ]

    if new_item_types:
        query = insert(item_type).values(new_item_types)
        await database.execute(query)
        print(f"New item types inserted successfully: {new_item_types}")
    else:
        print("All item types already exist. No new types inserted.")


async def get_item_type_id_by_name(item_type_name: str):
    query = select(item_type.c.id).where(item_type.c.description == item_type_name)
    result = await database.fetch_one(query)
    if result:
        return result["id"]
    else:
        raise ValueError(f"Item type '{item_type_name}' not found.")


async def get_item_type_name_by_id(type_id: int):
    query = select(item_type).where(item_type.c.id == type_id)
    result = await database.fetch_one(query)
    if result:
        return result['description']
    return None


async def get_item_type_by_name(name: str):
    query = select(item_type).where(item_type.c.description == name)
    return await database.fetch_one(query)


async def search_items_in_db(query: str):
    # Searching in title and description columns of the 'products' table
    search_query = select(products).where(
        (products.c.title.ilike(f'%{query}%')) |
        (products.c.description.ilike(f'%{query}%')) &
        (products.c.status != "Deleted")
    )

    result = await database.fetch_all(search_query)
    return result


async def post_edited_product_item(
                    product_id: int,
                    title: str,
                    description: str,
                    price: float,
                    discount: Optional[float],
                    quantity: int,
                    is_featured: str,
                    gender_category: GenderCategory,
                    item_type_id: str,
                    image_filename: str,
                    status: str
                    ):
    query = products.update().where(products.c.id == product_id).values(
        title=title,
        description=description,
        price=price,
        discount=discount,
        quantity=quantity,
        is_featured=is_featured,
        gender_category=gender_category,
        item_type_id=item_type_id,
        image_filename=image_filename,
        status=status
    )
    await database.execute(query)


async def get_product_by_id(product_id: int):
    query = select(products).where(products.c.id == product_id)
    result = await database.fetch_one(query)
    return result


async def get_all_items():
    query = select(products).where(products.c.status != "Deleted")
    result = await database.fetch_all(query)
    all_items = []
    for row in result:
        all_items.append({
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": Decimal(row["price"]),
            "discount": Decimal(row["discount"]) if row["discount"] else Decimal(0)
        })

    return all_items


async def get_items_by_category(gender: str, item_type_in: Optional[str] = None):
    if item_type_in:
        item_type_id = await get_item_type_id_by_name(item_type_in)
        if item_type_id is None:
            print(f"No item type found for {item_type_in}")
            return []
        query = select(products).where(
            (products.c.gender_category == gender) &
            (products.c.item_type_id == item_type_id) &
            (products.c.status != "Deleted")
        )
    else:
        query = select(products).where(
            (products.c.gender_category == gender) &
            (products.c.status != "Deleted")
        )

    result = await database.fetch_all(query)

    if not result:
        print(f"No items found for {gender} - {item_type_in}")

    items_by_category = []
    for row in result:
        items_by_category.append({
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": Decimal(row["price"]),
            "discount": Decimal(row["discount"]) if row["discount"] else Decimal(0)
        })
    return items_by_category


async def load_featured_items():
    query = select(products).where(
        (products.c.is_featured == 'featured') &
        (products.c.status != "Deleted")
    )
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
            "price": Decimal(row["price"]),
            "discount": Decimal(row["discount"]) if row["discount"] else Decimal(0)
        })

    return featured_items


async def add_item(item_in):
    query = products.insert().values(**item_in.model_dump())
    return await database.execute(query)


async def create_user(user_in):
    query = users.insert().values(**user_in.model_dump(exclude={"created_at"}))
    last_record_id = await database.execute(query)
    return {**user_in.model_dump(), "id": last_record_id}


async def get_users(skip: int = 0, limit: int = 10):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_user_by_login_data(email: str, password: str):
    query = users.select().where(users.c.email == email).where(users.c.password == password)
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def update_user(user_id: int, new_user):
    query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
    await database.execute(query)
    return {**new_user.model_dump(), "id": user_id}


async def add_newsletter_mail(newsletter_in):
    query = newsletter_subscriptions.insert().values(**newsletter_in.model_dump(exclude={"created_at"}))
    await database.execute(query)


async def create_position(position_in):
    query = positions.insert().values(**position_in.model_dump(exclude={"created_at"}))
    await database.execute(query)


async def get_positions(skip: int = 0, limit: int = 10):
    query = positions.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_position_by_id(position_id: int):
    query = positions.select().where(positions.c.id == position_id)
    return await database.fetch_one(query)


async def add_token_to_blacklist(token_in):
    query = tokens.insert().values(**token_in.model_dump())
    await database.execute(query)


async def get_token(token):
    query = tokens.select().where(positions.c.token == token)
    await database.fetch_one(query)
