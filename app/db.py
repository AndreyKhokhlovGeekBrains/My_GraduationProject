# database configuration
import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///mydatabase.db"
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

database = databases.Database(DATABASE_URL)



async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()
