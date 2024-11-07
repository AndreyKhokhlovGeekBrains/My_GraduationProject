# form handling routes
from fastapi import UploadFile
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles

from app.db import database
from cart.redis_client import get_unique_item, redis_get_from_cart, redis_clear_cart
from cookie.jwt import create_token, decode_token, JWT_EXPIRE
from app.schemas import (UserIn, NewsletterIn, TokenIn, ItemIn, GenderCategory, OrderIn, CardIn, Statuses,
                         OrderInReq)
from pydantic import EmailStr
from app.crud import (create_user, get_user_by_id, update_user, get_user_by_login_data, add_token_to_blacklist,
                      add_newsletter_mail, add_item, load_featured_items, get_items_by_category,
                      get_all_items, get_product_by_id, post_edited_product_item, search_items_in_db,
                      get_item_type_name_by_id, get_item_type_id_by_name, is_user_have_card,
                      add_order_to_db, add_card, get_item_by_id, create_order)

import bcrypt
import logging
from datetime import datetime

import json

from decimal import Decimal

logging.basicConfig(level=logging.INFO)
router = APIRouter()

templates = Jinja2Templates(directory="templates")

count = 0
    

# A mapping dictionary for specific item types
ITEM_TYPE_MAPPINGS = {
    "t_shirts": "T-Shirts",
    "jackets_coats": "Jackets & Coats"
}


@router.get("/search")
async def search_database_for_items(query: str, request: Request):
    # Check if the query is empty
    if not query.strip():
        # Show a message for empty queries
        return templates.TemplateResponse(request, "search_results.html", {
            "items": [],
            "count": count,
            "query": query,
            "message": "Please enter a search term"
        })

    # Proceed with normal search if query is not empty
    items = await search_items_in_db(query)
    return templates.TemplateResponse(request, "search_results.html", {
        "items": items,
        "count": count,
        "query": query
    })


@router.get("/edit-user-request")
async def get_edit_user_request(request: Request):
    return templates.TemplateResponse(request, "edit_user_request.html", {
        "count": count,
        "title": "Edit user request"
    })


@router.post("/edit-user-request")
async def post_edit_user_request(user_id: int = Form(...)):
    return RedirectResponse(f"/edit-user/{user_id}", status_code=303)


@router.get("/edit-request")
async def get_edit_request(request: Request):
    return templates.TemplateResponse(request, "edit_request.html", {
        "count": count,
        "title": "Edit product request"
    })


@router.post("/edit-request")
async def post_edit_request(product_id: int = Form(...)):
    current_product = await get_product_by_id(product_id)
    if current_product is None:
        return RedirectResponse(url="/edit-request?not_found=true", status_code=303)
    return RedirectResponse(f"/edit-item/{product_id}", status_code=303)


@router.get("/edit-user/{user_id}")
async def get_edit_user_form(user_id: int, request: Request):
    user_to_edit = await get_user_by_id(user_id)
    if user_to_edit:
        print(f"User found: {user_to_edit}")
    else:
        print(f"No user found with ID {user_id}")
    return templates.TemplateResponse(request, "edit_user.html", {
        "count": count,
        "user": user_to_edit,
        "title": "Edit user form"
    })


@router.post("/edit-user/{user_id}")
async def post_edit_user_form(
        user_id: int,
        input_name: str = Form(...),
        input_email: EmailStr = Form(...),
        input_password: str = Form(None),
        input_birthdate: str = Form(...),
        input_phone: str = Form(...),
        status: str = Form(...)
        ):
    current_user = await get_user_by_id(user_id)
    new_password = input_password if input_password else None
    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        hashed_password = current_user["password"]

    birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()

    new_user = UserIn(
            name=input_name if input_name else current_user["name"],
            email=input_email if input_email else current_user["input_email"],
            password=hashed_password,
            birthdate=birthdate if birthdate else current_user["birthdate"],
            phone=input_phone if input_phone else current_user["input_phone"],
            agreement=current_user["agreement"],
            status=status
        )

    logging.info(f'user_id: {user_id}')
    try:
        await update_user(user_id, new_user)
        return RedirectResponse(f"/edit-user-request?success=true", status_code=303)
    except Exception as e:
        logging.error(f"Failed to update user {user_id}: {e}")
        return RedirectResponse(f"/edit-user/{user_id}?success=false", status_code=303)


@router.get("/edit-item/{product_id}")
async def get_edit_item_form(product_id: int, request: Request):
    item_in = await get_product_by_id(product_id)
    return templates.TemplateResponse(request, "edit_item.html", {
        "count": count,
        "item": item_in,
        "title": "Edit product form"
    })


@router.post("/edit-item/{product_id}")
async def edit_item(product_id: int,
                    title: str = Form(None),
                    description: str = Form(None),
                    price: float = Form(None),
                    discount: Optional[float] = Form(None),
                    quantity: int = Form(None),
                    is_featured: str = Form(None),
                    gender_category: GenderCategory = Form(None),
                    item_type: str = Form(None),
                    image: Optional[UploadFile] = Form(None),
                    status: str = Form(None)):
    item_type_in = ITEM_TYPE_MAPPINGS.get(item_type.lower(), item_type.capitalize())
    current_product = await get_product_by_id(product_id)
    item_type_id = await get_item_type_id_by_name(item_type_in)

    image_filename = current_product['image_filename']
    if image:
        image_filename = image.filename

    try:
        # Fetch the `item_type_id` based on the selected item type name
        await post_edited_product_item(
            product_id=product_id,
            title=title if title else current_product["title"],
            description=description if description else current_product["description"],
            price=price if price else current_product["price"],
            discount=discount,
            quantity=quantity if quantity else current_product["quantity"],
            is_featured=is_featured if is_featured else current_product["is_featured"],
            gender_category=GenderCategory(gender_category) if gender_category else current_product["gender_category"],
            item_type_id=item_type_id,
            image_filename=image_filename if image_filename else current_product["image_filename"],
            status=status if status else current_product["status"]
        )
        return RedirectResponse(f"/edit-request?success=true", status_code=303)
    except Exception as e:
        logging.error(f"Failed to update user {product_id}: {e}")
        return RedirectResponse(f"/edit-item/{product_id}?success=false", status_code=303)


@router.get("/all")
async def get_all(request: Request):
    items_in = await get_all_items()
    return templates.TemplateResponse(request, "index.html", {
        "featured_items": items_in,
        "count": count,
        "show_all_items": True
    })


@router.get("/category/{gender}")
async def get_items_by_gender(request: Request, gender: str):
    items_in = await get_items_by_category(gender)
    return templates.TemplateResponse(request, "index.html", {
        "featured_items": items_in,
        "count": count,
        "gender": gender,
        "item_type": None
    })


@router.get("/category/{gender}/{item_type}")
async def get_items(request: Request, gender: str, item_type: str):
    # Check if the item_type exists in the mapping dictionary; if not, capitalize it
    item_type_in = ITEM_TYPE_MAPPINGS.get(item_type.lower(), item_type.capitalize())
    items_in = await get_items_by_category(gender, item_type_in)
    return templates.TemplateResponse(request, "index.html", {
        "featured_items": items_in,
        "count": count,
        "gender": gender,
        "item_type": item_type_in
    })


router.mount("/static", StaticFiles(directory="static"), name="static")


# def hash_password(password: str) -> str:
#     # Создание хеша
#     hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
#     return hashed_password.decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


@router.get("/add-item")
async def get_add_item_form(request: Request):
    return templates.TemplateResponse(request, "add_item.html", {"count": count})


@router.post("/add-item")
async def add_item_from_form(
    request: Request,  # noqa
    title: str = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    price: float = Form(...),
    discount: Optional[float] = Form(None),
    is_featured: str = Form(...),
    gender_category: GenderCategory = Form(...),
    item_type: str = Form(...),
    image: UploadFile = Form(...)
):
    image_filename = None
    if image:
        image_filename = image.filename

    item_type_in = ITEM_TYPE_MAPPINGS.get(item_type.lower(), item_type.capitalize())
    item_type_id = await get_item_type_id_by_name(item_type_in)

    # Create the item
    item_in = ItemIn(
        title=title,
        description=description,
        quantity=quantity,
        price=price,
        discount=discount,
        is_featured=is_featured,
        gender_category=gender_category,
        item_type_id=item_type_id,
        image_filename=image_filename  # Store the image filename in the database
    )
    item_id = await add_item(item_in)
    return RedirectResponse("/add-item?success=true", status_code=303)


@router.get("/")
async def html_index(request: Request):
    nickname = ""
    token = request.cookies.get("JWT")
    global count

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username

    featured_items = await load_featured_items()
    return templates.TemplateResponse(request, "index.html", {
        "count": count,
        "nickname": nickname,
        "featured_items": featured_items,
        "show_all_items": False,
        "title": "Main page"
    })


@router.get("/form/")
async def form(request: Request):
    global count
    nickname = ""
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username

    return templates.TemplateResponse(request, "input_form.html", {"count": count, "nickname": nickname})


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
    if not input_name:
        return templates.TemplateResponse(request, "input_form.html", {"error": "Введите имя!"})

    try:
        # Parse the birthdate from string to a date object
        birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()

        hashed_password = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            password=hashed_password,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )
        # Create the user
        created_user = await create_user(user_in)

        # Generate the JWT token for the registered user
        token = create_token(user_id=created_user["id"], user_email=created_user["email"],
                             username=created_user["name"])

        # Set up a redirect response and set the JWT token in the cookies
        response = RedirectResponse(url="/?success=true", status_code=303)
        response.set_cookie(key="JWT", value=token, httponly=True)  # Set the JWT token as an HTTP-only cookie

        return response

    except ValueError as e:
        # Handle errors such as incorrect age, birthdate, or missing data
        return templates.TemplateResponse(request, "input_form.html",
                                          {"error": f'Ошибка валидации данных: {str(e)}'})

    except Exception as e:
        return templates.TemplateResponse(request, "input_form.html", {"error": f'Ошибка: {str(e)}'})


@router.post("/logout/")
async def logout(request: Request):
    global count
    token = request.cookies.get("JWT")
    response = Response(status_code=200)  # 200 OK status for AJAX response

    if token:
        token_in = TokenIn(token=token)
        response.delete_cookie("JWT")
        await add_token_to_blacklist(token_in=token_in)

    # Reset cart count to zero after logout
    count = 0
    return response


@router.get("/login/")
async def login_page(request: Request):
    global count
    nickname = ""
    token = request.cookies.get("JWT")

    if token:
        decoded_token = decode_token(token)
        user_id = decoded_token.id
        count = get_unique_item(user_id)
        nickname = decoded_token.username

    return templates.TemplateResponse(request, "login_form.html", {
        "count": count,
        "nickname": nickname
    })


@router.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    token = request.cookies.get("JWT")
    response = RedirectResponse(url="/?success=true", status_code=303)
    if token is not None:
        response.delete_cookie("JWT")

    try:
        email, password = form_data["email"], form_data["password"]
        current_user = await get_user_by_login_data(email=email)
        if not current_user or not verify_password(password, current_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = int(current_user["id"])
        user_email = str(current_user["email"])
        username = str(current_user["name"])
        token = create_token(user_id=user_id, user_email=user_email, username=username)

        response.set_cookie(
            key="JWT",
            value=token,
            httponly=False,  # Prevents JavaScript access
            secure=True,  # Only sends cookie over HTTPS
            max_age=JWT_EXPIRE * 60,  # Expire time in seconds
            samesite="strict"  # CSRF protection
        )
        return response

    except Exception as e:
        print(e)
        return {'msg': "user not exists"}


@router.post("/add-order/")
async def add_order(
    request: Request,
    address: str = Form(...),  # Retrieve the address from the form submission
):
    # Retrieve the JWT from cookies
    token = request.cookies.get("JWT")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Decode the token to get the user information
    decoded_token = decode_token(token)
    user_id = decoded_token.id

    # Retrieve the items from the user's cart
    cart_content = redis_get_from_cart(user_id=user_id)
    if not cart_content:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Use the create_order function to handle the order creation
    order, order_items = await create_order(user_id, address, cart_content)

    # Clear the user's cart after the order is placed
    redis_clear_cart(user_id)

    # Redirect to a confirmation page
    return RedirectResponse(url="/order-confirmation", status_code=303)


@router.get("/order-form/")
async def order_form(request: Request):
    global count
    # Retrieve the JWT from cookies to identify the user
    token = request.cookies.get("JWT")
    if not token:
        # Redirect to login if the user is not authenticated
        return RedirectResponse("/login/")

    # Decode the JWT token to get user information
    decoded_token = decode_token(token)
    user_id = decoded_token.id

    # Retrieve the items in the cart from Redis
    cart_content = redis_get_from_cart(user_id=user_id)
    if not cart_content:
        # If the cart is empty, redirect back to the cart page
        return RedirectResponse("/cart/")

    # Initialize variables to store item details and total amount
    items = []
    total_amount = 0.0

    # Iterate through the items in the cart to fetch details from the database
    for item_id, quantity in cart_content.items():
        item = await get_item_by_id(item_id)
        if not item:
            continue  # Skip if the item is not found

        quantity = int(quantity)
        item_total = quantity * float(item.price) * (1 - (float(item.discount) or 0))
        total_amount += item_total

        # Append the item details to the list
        items.append({
            "id": item.id,
            "title": item.title,
            "price": item.price,
            "discount": item.discount,
            "image_filename": item.image_filename,
            "quantity": quantity,
            "item_total": item_total
        })

    # Render the order form template with the items and total amount
    return templates.TemplateResponse("order_form.html", {
        "request": request,
        "items": items,
        "total_amount": total_amount,
        "content": cart_content,
        "count": count
    })


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
