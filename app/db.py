# database configuration
import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///mydatabase.db"
# DATABASE_URL = "postgresql://user:password@localhost/dbname"
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()
