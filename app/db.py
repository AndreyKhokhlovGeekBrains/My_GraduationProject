# database configuration
from databases import Database
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Use environment variable to switch between local and Docker environments
DATABASE_URL = "postgresql://postgres:68064911@localhost:5432/postgres"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()
