# form handling routes
from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from cart.redis_client import get_unique_positions
import hashlib
from cookie.jwt import create_token, decode_token
from app.schemas import UserIn, TokenIn
from pydantic import EmailStr
from app.crud import create_user, get_user_by_login_data, add_token_to_blacklist
import httpx
# import bcrypt
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="templates")

<<<<<<< HEAD
count = 0


@router.get("/")
async def html_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "count": count})
=======
import hashlib


def hash_password(password: str) -> str:
    # Кодирование пароля в байты
    password_bytes = password.encode('utf-8')

    # Создание объекта хеширования
    hash_object = hashlib.sha256()

    # Обновление объекта хеширования
    hash_object.update(password_bytes)

    # Получение хеша
    hashed_password = hash_object.hexdigest()

    return hashed_password


def verify_password(stored_password: str, input_password: str) -> bool:
    # Хеширование входящего пароля
    hashed_input_password = hash_password(input_password)

    # Сравнение хешей
    return hashed_input_password == stored_password

@router.get("/")
async def html_index(request: Request):
    token = request.cookies.get("JWT")
    if token:
        decoded_token = decode_token(token)
        positions_amount = get_unique_positions(decoded_token.id)
        return templates.TemplateResponse("index.html", {"request": request, "counter": positions_amount})
    return templates.TemplateResponse("index.html", {"request": request})
>>>>>>> ea4a09d2c20a4d9611a5515123ba27b2c23e7a21


@router.get("/form/")
async def form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request": request, "count": count})


@router.post("/form/")
async def submit_form(
        request: Request,
        input_name: str = Form(..., alias="input-name", description="Name of the user"),
        input_email: EmailStr = Form(..., alias="input-email", description="Email of the user"),
        input_password: str = Form(..., alias="input-password", description="Password of the user"),
        input_age: int = Form(..., ge=1, alias="input-age", description="Age must be a positive integer"),
        input_birthdate: str = Form(..., alias="input-birthdate", description="Birthdate in YYYY-MM-DD format"),
        input_phone: str = Form(..., alias="input-phone", description="Phone number"),
        input_checkbox: str = Form(None, alias="input-checkbox")  # This will be 'on' if checked
):
    # Simple validation for name, feel free to extend validation to other fields
    if not input_name:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": "Введите имя!"})

    try:
        # Parse the birthdate from string to a date object
        birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()
        hashed_password = hash_password(input_password)
        # input_password_hashed = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            hashed_password=hashed_password,
            # password=input_password_hashed,
            age=input_age,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )
        # Удалить этот коментарий1
        # Call the create_user function
        await create_user(user_in)
        print(f"Created user: {user_in}")

        # Redirect to the home page or another page after successful submission
        return RedirectResponse(url="/", status_code=303)
        # return RedirectResponse(url=f"/user/{created_user['id']}", status_code=303)

    except ValueError as e:

        return templates.TemplateResponse("input_form.html",
                                          {"request": request, "error": f'Ошибка валидации данных: {str(e)}'})

    except Exception as e:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": f'Ошибка: {str(e)}'})


@router.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login_form.html", {"request": request, "count": count})


@router.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    token = request.cookies.get("JWT")
    response = Response(content="Login successful!")
    response.delete_cookie("JWT")
    if token is not None:
        await add_token_to_blacklist(token)

    try:
        email, password = form_data["email"], form_data["password"]
        hashed_password = hash_password(password)
        current_user = await get_user_by_login_data(email=email, password=hashed_password)

        if verify_password(hashed_password, password):
            user_id, user_email, username = current_user["id"], current_user["email"], current_user["name"]
            token = create_token(user_id=user_id, user_email=user_email, username=username)
            print(token)

            response.set_cookie(key="JWT", value=token)
            return response

    except TypeError:
        return {'msg': "user not exists"}


@router.get("/logout/")
async def logout_page(request: Request):
    if request.cookies.get("JWT"):
        return templates.TemplateResponse("logout.html", {"request": request})
    return RedirectResponse(url="/login/")


@router.post("/logout/")
async def logout(request: Request):
    token = request.cookies.get("JWT")
    response = Response(status_code=200)
    token_in = TokenIn(token=token)
    response.delete_cookie("JWT")
    await add_token_to_blacklist(token_in=token_in)
    return RedirectResponse(url="/")


@router.get("/test_confident1/")
async def confident1(request: Request):
    token = request.cookies.get("JWT")
    if token:
        return {"test_confident1": True}
    return {"test_confident1": False}
