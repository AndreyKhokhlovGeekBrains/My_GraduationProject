# form handling routes
from fastapi import APIRouter, Request, Form, Response, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request, Form, Response, Depends, Body
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles

from cart.redis_client import get_unique_item
from cookie.jwt import create_token, decode_token
from app.schemas import UserIn, NewsletterIn, TokenIn, ItemIn, GenderCategory, OrderIn, CardIn
from pydantic import EmailStr
from app.crud import (create_user, get_user_by_login_data, add_token_to_blacklist,
                      add_newsletter_mail, add_item, load_featured_items, get_items_by_category, get_all_items,
                      is_user_have_card, add_order_to_db, add_card, get_item_by_id, find_items_by_name)
import shutil
from app.schemas import UserIn, TokenIn, NewsletterIn, ItemIn, OrderIn, Statuses
from pydantic import EmailStr, BaseModel
from app.crud import create_user, get_user_by_login_data, add_token_to_blacklist, get_token
import httpx
import bcrypt
from datetime import datetime

import json

from decimal import Decimal


router = APIRouter()

templates = Jinja2Templates(directory="templates")

count = 0


class Order(BaseModel):
    address: str
    item_name: str
    item_id: str
    item_quantity: int
    item_price: Decimal


class Card(BaseModel):
    card_owner: str
    card_number: str
    card_exp_date: str
    card_cvv: str


@router.get("/all")
async def get_all(request: Request):
    items_in = await get_all_items()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "show_all_items": True
    })


@router.get("/category/{gender}")
async def get_items_by_gender(request: Request, gender: str):
    items_in = await get_items_by_category(gender)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "gender": gender,
        "item_type": None
    })


@router.get("/category/{gender}/{item_type}")
async def get_items(request: Request, gender: str, item_type: str):
    items_in = await get_items_by_category(gender, item_type)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "gender": gender,
        "item_type": item_type
    })


@router.get("/search/")
async def get_items_by_name(request: Request, name: str):
    items_in = await find_items_by_name(name)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_items": items_in,
        "count": count,
        "show_all_items": True
    })


router.mount("/static", StaticFiles(directory="static"), name="static")


def hash_password(password: str) -> str:
    # Создание хеша
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    return hashed_password.decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


@router.get("/")
async def html_index(request: Request):
    count = 0
    nickname = ""
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username
    featured_items = await load_featured_items()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "count": count,
        "nickname": nickname,
        "featured_items": featured_items,
        "show_all_items": False
    })


@router.get("/add-item")
async def get_add_item_form(request: Request):
    return templates.TemplateResponse("add_item.html", {"request": request, "count": count})


@router.post("/add-item")
async def add_item_from_form(
    request: Request,  # noqa
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    discount: Optional[float] = Form(None),
    is_featured: str = Form(...),
    gender_category: GenderCategory = Form(...),
    item_type: str = Form(...),
    image: UploadFile = Form(...)
):
    # Save the uploaded image to the static folder
    image_filename = None
    if image:
        image_filename = image.filename

    # Create the item
    item_in = ItemIn(
        title=title,
        description=description,
        price=price,
        discount=discount,
        is_featured=is_featured,
        gender_category=gender_category,
        item_type=item_type,
        image_filename=image_filename  # Store the image filename in the database
    )
    await add_item(item_in)
    return RedirectResponse("/add-item?success=true", status_code=303)


@router.get("/form/")
async def form(request: Request):
    count = 0
    nickname = ""
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username

    return templates.TemplateResponse("input_form.html", {"request": request, "count": count, "nickname": nickname})


@router.post("/form/")
async def submit_form(
        request: Request,
        input_name: str = Form(..., alias="input-name", description="Name of the user"),
        input_email: EmailStr = Form(..., alias="input-email", description="Email of the user"),
        input_password: str = Form(..., alias="input-password", description="Password of the user"),
        input_birthdate: str = Form(..., alias="input-birthdate", description="Birthdate in YYYY-MM-DD format"),
        input_phone: str = Form(..., alias="input-phone", description="Phone number"),
        input_checkbox: str = Form(None, alias="input-checkbox")  # This will be 'on' if checked
):
    # Simple validation for name, feel free to extend validation to other fields
    if not input_name:
        return templates.TemplateResponse("input_form.html", {"request": request, "error": "Введите имя!"})
    count = 0
    try:
        # Parse the birthdate from string to a date object
        birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()
        # hashed_password = hash_password(input_password)
        # input_password_hashed = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            password=hash_password(input_password),
            # password=input_password_hashed,
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
        print("ValueError: ", e)
        return templates.TemplateResponse("input_form.html",
                                          {"request": request, "error": f'Ошибка валидации данных: {str(e)}',
                                           "count": count})

    except Exception as e:
        print("Exception: ", e)
        return templates.TemplateResponse("input_form.html", {"request": request, "error": f'Ошибка: {str(e)}',
                                                              "count": count})


@router.get("/login/")
async def login_page(request: Request):
    count = 0
    nickname = ""
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username

    return templates.TemplateResponse("login_form.html", {"request": request, "count": count, "nickname": nickname})


@router.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    token = request.cookies.get("JWT")

    if token is not None:
        print(token)
        # Здесь можно добавить логику для работы с устаревшими токенами, если нужно

    try:
        email, password = form_data["email"], form_data["password"]
        print(email)
        print(password)
        current_user = await get_user_by_login_data(email=email)
        if not current_user or not verify_password(password, current_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = int(current_user["id"])
        user_email = str(current_user["email"])
        username = str(current_user["name"])
        token = create_token(user_id=user_id, user_email=user_email, username=username)
        print(f"Token: {token}")

        response = RedirectResponse(url="/login?success=true", status_code=303)
        response.set_cookie(key="JWT", value=token, httponly=True)  # Устанавливаем cookie с токеном

        return response

    except Exception as e:
        print(e)
        return {'msg': "user not exists"}


@router.get("/logout/")
async def logout_page(request: Request):
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username
        return templates.TemplateResponse("logout.html", {"request": request, "count": count, "nickname": nickname})
    return RedirectResponse(url="/login/")


@router.post("/logout/")
async def logout(request: Request):
    token = request.cookies.get("JWT")
    print(token)
    if token:
        response = Response(status_code=302)
        response.headers["Location"] = "http://127.0.0.1:8000/"
        token_in = TokenIn(token=token)
        response.delete_cookie("JWT")
        await add_token_to_blacklist(token_in=token_in)
        # return RedirectResponse(url="/")
        return response
    return RedirectResponse(url="/login/")


@router.get("/add-order/")
async def add_order_page(request: Request):
    token = request.cookies.get("JWT")
    if token:
        decoded_token = decode_token(token)

        # Получаем параметры из запроса
        item_id = request.query_params.get("item_id")
        item_amount = request.query_params.get("amount")
        item_name = request.query_params.get("itemName")
        price = request.query_params.get("price")
        print(item_id)
        print(item_amount)
        print(item_name)
        print(price)

        # Проверяем, были ли переданы необходимые параметры
        if item_id is None or item_amount is None or item_name is None:
            raise HTTPException(status_code=400, detail="item_id, amount, and itemName are required")

        try:
            item_id = int(item_id)
            item_amount = int(item_amount)
        except ValueError:
            raise HTTPException(status_code=400, detail="item_id and amount must be integers")

        count = get_unique_item(decoded_token.id)
        nickname = decoded_token.username

        return templates.TemplateResponse("add_order.html", {
            "request": request,
            "itemId": item_id,
            "amount": item_amount,
            "user_id": decoded_token.id,
            "item_name": item_name,
            "count": count,
            "nickname": nickname,
            "price": price,
        })

    return RedirectResponse("/login/")


class OrderInReq(BaseModel):
    item_id: int
    amount: int
    itemName: str
    address: str


@router.post("/add-order/")
async def add_order(request: Request, order: OrderInReq):
    token = request.cookies.get("JWT")
    print(token)
    if not token:
        return RedirectResponse(url="/login/", status_code=303)

    decoded_token = decode_token(token)
    print(f"decoded_token: {decoded_token}, {decoded_token.id}")

    # Получение данных формы
    order_data = await request.json()
    print(order_data)

    # Теперь вы можете использовать order_data['item_id'], order_data['amount'] и т.д.
    item_id = order.item_id
    item_quantity = order.amount
    item_name = order.itemName  # noqa
    address = order.address

    # Получаем информацию о товаре из базы данных
    item_from_db = await get_item_by_id(int(item_id))
    item_price_str = item_from_db["price"]

    if item_from_db:
        # Проверяем, был ли передан item_id
        if item_id is None:
            raise HTTPException(status_code=400, detail="item_id is required")

        try:
            item_id = int(item_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="item_id must be an integer")

    # Проверяем, был ли передан item_quantity
        if item_quantity is None:
            raise HTTPException(status_code=400, detail="item_quantity is required")

        try:
            item_quantity = int(item_quantity)
        except ValueError:
            raise HTTPException(status_code=400, detail="item_quantity must be an integer")

    # Рассчитываем общую цену
    try:
        item_price = Decimal(int(item_price_str) * item_quantity)
        print(f"Item price: {item_price}")
    except Exception as e:
        print(f"Error calculating item price: {e}")
        raise HTTPException(status_code=500, detail="Error calculating item price")

    # Проверяем наличие карты у пользователя
    user_card = await is_user_have_card(decoded_token.id)
    print(Statuses.placing.value)
    print(f"User  card: {user_card}")
    if not user_card:
        print("No card found")
        return RedirectResponse(url="/add-card/", status_code=303)

    user_id = int(decoded_token.id)
    # Создаем объект OrderIn с правильным значением статуса
    order_in = OrderIn(
        user_id=user_id,
        item_id=item_id,
        amount=item_quantity,
        price=item_price,
        status=str(Statuses.placing.value),
        address=address,
    )

    # Добавляем заказ в базу данных
    order_id = await add_order_to_db(order_in)

    if not order_id:
        raise HTTPException(status_code=500, detail="Failed to create order")
    else:
        return {"success": True, "order_id": order_id}


@router.get("/add-card/")
async def add_cart_page(request: Request):
    token = request.cookies.get("JWT")
    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username
        return templates.TemplateResponse("add_card.html", {"request": request, "user_id": decoded_token.id,
                                                            "count": count, "nickname": nickname})

    return RedirectResponse("/login/")


@router.post("/add-card/")
async def add_cart(request: Request):
    token = request.cookies.get("JWT")
    try:
        request_body = await request.body()
        request_body = json.loads(request_body.decode("utf-8"))

        card_owner = request_body["card_owner"]
        card_number = request_body["card_number"]
        card_cvv = request_body["cvv"]
        card_exp_date = request_body["expiry_date"]

        if token:
            decoded_token = decode_token(token)
            card_in = CardIn(
                user_id=int(decoded_token.id),
                card_owner=str(card_owner),
                card_number=str(card_number),
                card_cvv=str(card_cvv),
                card_exp_date=str(card_exp_date)
            )
            card_db = await add_card(card_in)
            return {"success": True, "card": card_db}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse("/login/", status_code=303)


@router.post("/subscribe/")
async def subscribe(
        email: EmailStr = Form(...)
):
    newsletter_in = NewsletterIn(email=email)
    await add_newsletter_mail(newsletter_in)
    print(f"Created mail: {newsletter_in}")
    return RedirectResponse(url="/", status_code=303)
