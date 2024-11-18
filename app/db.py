# database configuration
from databases import Database
import sqlalchemy

DATABASE_URL = "postgresql://postgres:68064911@localhost:5432/postgres"

engine = sqlalchemy.create_engine(url=DATABASE_URL)
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()
