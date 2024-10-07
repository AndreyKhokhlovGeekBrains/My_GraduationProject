# user-related routes
from fastapi import APIRouter, Depends
from app.schemas import UserIn, User
from app.crud import create_user, get_users, get_user_by_login_data, update_user, delete_user, get_user_by_id
from typing import List

router = APIRouter()


@router.post("/", response_model=User)
async def create_user_route(user_in: UserIn):
    return await create_user(user_in)


@router.get("/", response_model=List[User])
async def get_users_route(skip: int = 0, limit: int = 10):
    return await get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
async def get_user_route(user_id: int):
    return await get_user_by_id(user_id)


@router.put("/{user_id}", response_model=User)
async def update_user_route(user_id: int, new_user: UserIn):
    return await update_user(user_id, new_user)


@router.delete("/{user_id}")
async def delete_user_route(user_id: int):
    return await delete_user(user_id)
