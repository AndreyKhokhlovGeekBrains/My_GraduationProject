from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from .redis_client import redis_get_from_cart, redis_add_to_cart, redis_remove_from_cart
from cookie.jwt import decode_token

router = APIRouter(prefix="/cart", tags=["cart"])

templates = Jinja2Templates(directory="templates")

@router.get("/get/")
async def get_cart(request: Request):
    token = request.cookies.get("JWT")
    if token:
        decoded_token = decode_token(token)
        content = redis_get_from_cart(user_id=decoded_token.id)
        return templates.TemplateResponse("cart.html", {"request": request, "content": content})
    return RedirectResponse("/login/")

@router.get("/add/")
async def add_cart(request: Request):
    token = request.cookies.get("JWT")
    if token:
        position_id = int(request.query_params.get("position_id"))
        amount = int(request.query_params.get("amount"))
        decoded_token = decode_token(token)
        status = redis_add_to_cart(user_id=decoded_token.id, position_id=position_id, amount=amount)
        if status["status"] == 200:
            return status.update({"msg": "Position successful added to cart!"})
    return RedirectResponse("/login/")

@router.get("/delete/")
async def del_cart(request: Request):
    token = request.cookies.get("JWT")
    if token:
        position_id = int(request.query_params.get("position_id"))
        amount = int(request.query_params.get("amount"))
        decoded_token = decode_token(token)
        status = redis_remove_from_cart(user_id=decoded_token.id, position_id=position_id, amount=amount)
        if status["status"] == 200:
            return status.update({"msg": "Position successful added to cart!"})
    return RedirectResponse("/login/")
