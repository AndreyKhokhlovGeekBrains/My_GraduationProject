# database operations
from cart.redis_client import client
from .models import users, newsletter_subscriptions, tokens, products, item_type, orders, order_items
from .db import database
from sqlalchemy import select, insert, update
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


async def get_quantity(product_id: int):
    query = select(products.c.id, products.c.quantity).where(products.c.id == product_id)
    result = await database.fetch_one(query)
    if result:
        return result["quantity"]
    else:
        raise ValueError(f'Product with id {product_id} not found')


async def set_quantity(product_id: int, new_quantity: int):
    query = select(products.c.id).where(products.c.id == product_id)
    result = await database.fetch_one(query)
    if result:
        update_query = (
            update(products)
            .where(products.c.id == product_id)
            .values(quantity=new_quantity)
        )
        await database.execute(update_query)
        print(f'Set quantity for product with id {product_id} to {new_quantity}')
    else:
        raise ValueError(f'Product with id {product_id} not found')


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


# async def is_user_have_card(user_id: int):
#     query = select(cards).where(cards.c.user_id == user_id)
#     return await database.fetch_one(query)


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
            "id": row["id"],
            "picture": f"/static/img/featured_items/{row['image_filename']}",
            "title": row["title"],
            "description": row["description"],
            "price": Decimal(row["price"]),
            "discount": Decimal(row["discount"]) if row["discount"] else Decimal(0)
        })

    return featured_items


async def add_item(item_in):
    query = products.insert().values(**item_in.model_dump())
    item_id = await database.execute(query)
    # Check that the item was successfully added by querying for its existence
    if item_id is not None:
        select_query = select(products).where(products.c.id == item_id)
        item_record = await database.fetch_one(select_query)
        if item_record is None:
            raise ValueError("Failed to verify the addition of the item to the database.")
    return item_id


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


async def get_item_id_by_title(item_title):
    query = products.select().where(products.c.title == item_title)
    try:
        product = await database.fetch_one(query)
        return product["id"] if product else None
    except Exception as e:
        print("Error fetching item by title:", e)
        return None


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
        query = users.insert().values(**user_in.model_dump(exclude={"created_at"}))
        last_record_id = await database.execute(query)
        return {**user_in.model_dump(), "id": last_record_id}
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
    query = users.update().where(users.c.id == user_id).values(**new_user.model_dump())
    await database.execute(query)
    return {**new_user.model_dump(), "id": user_id}


async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)


# async def add_order_to_db(order_in):
#     print("Creating order:", order_in.dict())
#     query = orders.insert().values(**order_in.dict())
#     return await database.execute(query)


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
    query = newsletter_subscriptions.insert().values(**newsletter_in.model_dump(exclude={"created_at"}))
    await database.execute(query)


async def add_token_to_blacklist(token_in):
    query = tokens.insert().values(**token_in.model_dump())
    await database.execute(query)


async def get_token(token):
    query = tokens.select().where(tokens.c.token == token)
    await database.fetch_one(query)


async def create_order(user_id: int, address: str, cart_content: dict):
    total_amount = 0.0
    order_items_list = []

    # Start a database transaction
    async with database.transaction():
        # Insert the order into the orders table
        order_insert_query = insert(orders).values(
            user_id=user_id,
            address=address,
            total_amount=total_amount  # Initial total, to be updated later
        )
        # Execute the insert query and get the order ID
        order_id = await database.execute(order_insert_query)

        # Iterate through the cart content and add items to the order
        for item_id, quantity in cart_content.items():
            # Fetch the item details from the database
            item = await get_item_by_id(item_id)
            if not item:
                continue  # Skip if the item is not found

            quantity = int(quantity)
            item_total = quantity * float(item.price) * (1 - float(item.discount or 0))
            total_amount += item_total

            # Insert the order item into the order_items table
            item_discount = float(item.discount or 0)

            order_item_insert_query = insert(order_items).values(
                order_id=order_id,
                product_id=item.id,
                price=float(item.price),
                discount=item_discount,
                quantity=quantity
            )
            await database.execute(order_item_insert_query)
            order_items_list.append({
                "order_id": order_id,
                "product_id": item.id,
                "price": float(item.price),
                "discount": item_discount,
                "quantity": quantity
            })

        # Update the total amount in the orders table
        update_query = orders.update().where(orders.c.id == order_id).values(total_amount=total_amount)
        await database.execute(update_query)

    return {"order_id": order_id, "order_items": order_items_list}


# a simple function to mock the validation of payment details.
# In a real-world scenario, you would integrate with a payment gateway like Stripe or PayPal
def validate_card_details(card_owner, card_number, expiry_date, cvv):
    # Implement real payment validation or integration with a payment gateway
    return True
