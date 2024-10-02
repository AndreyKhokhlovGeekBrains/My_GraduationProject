# form handling routes
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.schemas import UserIn
from pydantic import EmailStr
from app.crud import create_user
import httpx
# import bcrypt
from datetime import datetime

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def html_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/form/")
async def form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request": request})


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

        # input_password_hashed = bcrypt.hashpw(input_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_in = UserIn(
            name=input_name,
            email=input_email,
            password=input_password,
            # password=input_password_hashed,
            age=input_age,
            birthdate=birthdate,
            phone=input_phone,
            agreement=True if input_checkbox == 'on' else False
        )

        # Convert the date to string in YYYY-MM-DD format
        user_data = user_in.dict()
        user_data['birthdate'] = user_data['birthdate'].isoformat()  # Convert date to string

        # Send data to FastAPI
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8000/users/", json=user_data)
            response.raise_for_status()  # Raise an error for bad responses

        return RedirectResponse(url="/")

    except ValueError as e:
        # Handle errors such as incorrect age, birthdate, or missing data
        return templates.TemplateResponse("input_form.html",
                                          {"request": request, "error": f'Ошибка валидации данных: {str(e)}'})
    except httpx.HTTPStatusError as e:
        return templates.TemplateResponse("input_form.html", {"request": request,
                                                              "error": f'Ошибка при отправке данных на сервер: {str(e)}'})


@router.get("/login/")
async def form(request: Request):
    return templates.TemplateResponse("login_form.html", {"request": request})
