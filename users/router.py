from typing import Annotated

from fastapi import APIRouter, Response, Depends, Form

from exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, CannotAddDataToDatabase
from users.auth import get_password_hash, authenticate_user, create_access_token
from users.depends import get_current_user, get_curent_admin_user
from users.models import User
from users.schemas import SUserRegister, SUserAuth
from users.service import UserService
from fastapi_versioning import version


router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router_users = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@version(1)

@router_auth.post("/register", status_code=201)
async def register_user(email: Annotated[str, Form()], password: Annotated[str, Form()]):
    existing_user = await UserService.find_one_or_none(email=email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(password)
    new_user = await UserService.add(email=email, hashed_password=hashed_password)
    if not new_user:
        raise CannotAddDataToDatabase

@version(1)
@router_auth.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.email, user_data.password)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return {"access_token": access_token}

@version(1)
@router_auth.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")

@version(1)
@router_users.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user