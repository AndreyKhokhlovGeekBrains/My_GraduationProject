import typer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import connect_db, disconnect_db, metadata, engine
from routes import users_router, forms
from cart import cart_router
import os


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routes
# app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(forms.router, tags=["forms"])
app.include_router(cart_router)


@app.on_event("startup")
async def startup():
    metadata.create_all(engine)  # Create tables on startup
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()


"""async def connect_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def disconnect_db():
    await engine.dispose()
"""


# uvicorn app.main:app --reload
# git push -u origin dev1
# pip install -r requirements.txt
# docker-compose up
# - ./pgdata:/var/lib/postgresql/data


# import psycopg2
#
# try:
#     conn = psycopg2.connect("postgresql://postgres:68064911@localhost:5432/postgres")
#     print("Connection successful")
#     conn.close()
# except Exception as e:
#     print("Connection failed")
#     print(e)
