from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.db import connect_db, disconnect_db, metadata, engine
from routes import forms
from cart import cart_router
from app.crud import populate_item_types
import os

# Use an absolute path for the static directory
static_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static"))
templates_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates"))

templates = Jinja2Templates(directory=templates_directory)


@asynccontextmanager
async def lifespan(app_in: FastAPI):
    # Startup logic
    await connect_db()
    metadata.create_all(engine)
    await populate_item_types()
    yield
    # Shutdown logic
    await disconnect_db()

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory=static_directory), name="static")
# Register routes
app.include_router(forms.router, tags=["forms"])
app.include_router(cart_router)


@app.exception_handler(Exception)
async def custom_500_handler(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return templates.TemplateResponse(request, "500.html", {
        "count": 0,
        "title": "Server Error"
    })


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    print(f"404 error: {request.url} not found.")
    return templates.TemplateResponse(request, "404.html", {
        "count": 0,
        "title": "Page Not Found"
    })


# uvicorn app.main:app --reload
# pip install -r requirements.txt
# docker-compose up
# - ./pgdata:/var/lib/postgresql/data
# /edit-user-request - a request to edit a user's info
# /edit-request - a request to edit a product's info
# /add-item - add a new product
