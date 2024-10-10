# database operations

#from .models import User, Car, Token
from .db import database


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
    
async def create_position(position_in):
    query = Car.insert().values(**position_in.dict())
    await database.execute(query)

async def get_positions(skip: int = 0, limit: int = 10):
    query = positions.select().offset(skip).limit(limit)
    return await Car.fetch_all(query)

async def get_position_by_id(car_id: int):
    query = Car.select().where(Car.id == car_id)
    return await database.fetch_one(query)

async def add_token_to_blacklist(token_in):
    query = Token.insert().values(**token_in.dict())
    await database.execute(query)

async def get_token(token):
    query = Token.select().where(Token.token == token)
    await  database.fetch_one(query)
