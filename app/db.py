# database configuration
from databases import Database
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Use environment variable to switch between local and Docker environments
DATABASE_URL = "postgresql://postgres:68064911@localhost:5432/postgres"

<<<<<<< HEAD
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
=======
database = databases.Database(DATABASE_URL)
>>>>>>> ea4a09d2c20a4d9611a5515123ba27b2c23e7a21



async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()
