# form handling routes
from fastapi import APIRouter, Request, Form, Response, UploadFile, FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from starlette.exceptions import HTTPException as StarletteHTTPException

from cookie.jwt import create_token, decode_token
from app.schemas import UserIn, NewsletterIn, TokenIn, ItemIn, GenderCategory
from pydantic import EmailStr
from app.crud import (create_user, get_user_by_id, update_user, get_user_by_login_data, add_token_to_blacklist,
                      add_newsletter_mail, add_item, load_featured_items, get_items_by_category,
                      get_all_items, get_product_by_id, post_edited_product_item, search_items_in_db,
                      get_item_type_name_by_id, get_item_type_id_by_name)

import bcrypt
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
router = APIRouter()

templates = Jinja2Templates(directory="templates")

count = 0

# A mapping dictionary for specific item types
ITEM_TYPE_MAPPINGS = {
    "tshirts": "T-Shirts",
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


@router.get("/add-item")
async def get_add_item_form(request: Request):
    return templates.TemplateResponse(request, "add_item.html", {"count": count})


@router.post("/add-item")
async def add_item_from_form(
    request: Request,
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
    # Save the uploaded image to the static folder
    image_filename = None
    if image:
        image_filename = image.filename

    item_type_id = await get_item_type_id_by_name(item_type)

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
    await add_item(item_in)
    return RedirectResponse("/add-item?success=true", status_code=303)


@router.get("/")
async def html_index(request: Request):
    featured_items = await load_featured_items()
    return templates.TemplateResponse(request, "index.html", {
        "count": count,
        "featured_items": featured_items,
        "show_all_items": False,
        "title": "Main page"
    })


@router.get("/form/")
async def form(request: Request):
    return templates.TemplateResponse(request, "input_form.html", {"count": count})


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
        return templates.TemplateResponse(request, "input_form.html", {"error": "Введите имя!"})

    try:
        # Parse the birthdate from string to a date object
        birthdate = datetime.strptime(input_birthdate, '%Y-%m-%d').date()

        hashed_password = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            # password=input_password,
            password=hashed_password,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )

        # Call the create_user function
        await create_user(user_in)
        print(f"Created user: {user_in.model_dump(exclude={'password'})}")

        # Redirect to the home page
        return RedirectResponse(url="/", status_code=303)
        # Or redirect to a page showing the new user's details
        # return RedirectResponse(url=f"/user/{created_user['id']}", status_code=303)

    except ValueError as e:
        # Handle errors such as incorrect age, birthdate, or missing data
        return templates.TemplateResponse(request, "input_form.html",
                                          {"error": f'Ошибка валидации данных: {str(e)}'})

    except Exception as e:
        return templates.TemplateResponse(request, "input_form.html", {"error": f'Ошибка: {str(e)}'})


@router.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login_form.html", {"count": count})


@router.post("/login/")
async def login_user(request: Request):
    form_data = await request.form()
    token = request.cookies.get("JWT")
    response = Response(content="Login successful!")
    response.delete_cookie("JWT")
    await add_token_to_blacklist(token)

    email, password = form_data["email"], form_data["password"]
    current_user = await get_user_by_login_data(email=email, password=password)
    user_id, user_email, username = current_user["id"], current_user["email"], current_user["name"]
    token = create_token(user_id=user_id, user_email=user_email, username=username)
    print(token)

    response.set_cookie(key="JWT", value=token)
    return response


@router.get("/logout/")
async def logout_page(request: Request):
    if request.cookies.get("JWT"):
        return templates.TemplateResponse(request, "logout.html", {})
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


@router.post("/subscribe")
async def subscribe(
        email: EmailStr = Form(...)
):
    newsletter_in = NewsletterIn(email=email)
    await add_newsletter_mail(newsletter_in)
    print(f"Created mail: {newsletter_in}")
    return RedirectResponse(url="/", status_code=303)
