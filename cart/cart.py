from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from .redis_client import (redis_get_from_cart, redis_add_to_cart, redis_remove_from_cart, get_unique_item,
                           redis_clear_cart)
from cookie.jwt import decode_token

from app.crud import get_item_by_id, get_items_by_ids


router = APIRouter(prefix="/cart", tags=["cart"])

templates = Jinja2Templates(directory="templates")


@router.get("/get/")
async def get_cart(request: Request):
    token = request.cookies.get("JWT")
    print(token)
    if token is not None:
        decoded_token = decode_token(token)
        content = redis_get_from_cart(user_id=decoded_token.id)
        count = get_unique_item(user_id=decoded_token.id)
        nickname = decoded_token.username
        print("Content: ", content)
        if content:
            items = await get_items_by_ids(list(content.keys()))
            print(f"items: {items}")
            if items == [None]:
                redis_clear_cart(decoded_token.id)  # Очистить корзину
                print("Cart cleared")
        else:
            items = None
        return templates.TemplateResponse("cart.html", {"request": request, "content": content, "count": count,
                                                        "items": items, "nickname": nickname})
    return RedirectResponse("/login/")


@router.post("/add/")
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


@router.post("/delete/")
async def del_cart(request: Request):
    token = request.cookies.get("JWT")
    if token:
        position_id = int(request.query_params.get("position_id"))
        amount = int(request.query_params.get("amount"))
        decoded_token = decode_token(token)
        response = redis_remove_from_cart(user_id=decoded_token.id, position_id=position_id, amount=amount)

        return {"msg": "Position successful deleted from cart!", "success": True, "status": response["status"]}
    return RedirectResponse("/login/")
