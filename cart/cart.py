from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .redis_client import (redis_get_from_cart, redis_add_to_cart, redis_remove_from_cart, get_unique_item,
                           redis_clear_cart, update_item_quantity_in_cart)
from app.schemas import QuantityUpdateRequest
from cookie.jwt import decode_token
from app.crud import get_item_by_id, get_items_by_ids, get_quantity
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/cart", tags=["cart"])

templates = Jinja2Templates(directory="templates")


@router.get("/get/")
async def get_cart(request: Request):
    token = request.cookies.get("JWT")
    if token is not None:
        decoded_token = decode_token(token)
        content = redis_get_from_cart(user_id=decoded_token.id)
        count = get_unique_item(user_id=decoded_token.id)
        nickname = decoded_token.username
        if content:
            items = await get_items_by_ids(list(content.keys()))
            if items == [None]:
                redis_clear_cart(decoded_token.id)  # Очистить корзину
                print("Cart cleared")
        else:
            items = None
        return templates.TemplateResponse(request, "cart.html", {
            "content": content,
            "count": count,
            "items": items,
            "nickname": nickname
        })
    return RedirectResponse("/login/")


@router.get("/add/")
@router.post("/add/")
async def add_cart(request: Request, position_id: int = None, amount: int = 1):
    token = request.cookies.get("JWT")

    # If the request is a GET request and the user is not logged in, redirect to login
    if not token:
        return RedirectResponse("/login/")

    # If the request is POST, then we expect a logged-in user
    if request.method == "POST":
        form = await request.form()
        position_id = int(form.get("position_id", position_id))
        amount = int(form.get("amount", amount))
    else:
        # Handle GET request (from unauthenticated users)
        position_id = int(request.query_params.get("position_id", position_id))
        amount = int(request.query_params.get("amount", amount))

    # Decode the JWT token and add the item to the cart if logged in
    decoded_token = decode_token(token)
    redis_add_to_cart(user_id=decoded_token.id, position_id=position_id, amount=amount)
    # Respond with a JSON message confirming success
    return JSONResponse(status_code=200, content={"msg": "Position successfully added to cart!"})


@router.post("/delete/")
async def del_cart(request: Request):
    token = request.cookies.get("JWT")
    if token:
        position_id = int(request.query_params.get("position_id"))
        decoded_token = decode_token(token)
        response = redis_remove_from_cart(user_id=decoded_token.id, position_id=position_id)

        return {"msg": "Position deleted from cart successfully!", "success": True, "status": response["status"]}
    return RedirectResponse("/login/")


@router.post("/update_quantity/")
async def update_cart_quantity(update_request: QuantityUpdateRequest, request: Request):
    item_id = update_request.item_id
    quantity = update_request.quantity
    max_quantity = await get_quantity(item_id)

    # print("Max quantity is: ", max_quantity)
    # print("Received item_id:", item_id)
    # print("Received quantity:", quantity)

    token = request.cookies.get("JWT")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    decoded_token = decode_token(token)

    if quantity <= max_quantity:
        success = update_item_quantity_in_cart(user_id=decoded_token.id, item_id=item_id, quantity=quantity)
        message = ""
    else:
        success = update_item_quantity_in_cart(user_id=decoded_token.id, item_id=item_id, quantity=max_quantity)
        message = f"Maximum quantity available: {max_quantity}"

    if success:
        return JSONResponse(content={"success": True, "message": message})
    else:
        return JSONResponse(content={"success": False, "message": "Failed to update quantity."})

