from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError, ExpiredSignatureError

from config import settings
from exceptions import TokenExpiredException, IncorrectTokenFormatException, UserIsNotPresentException
from users.models import User
from users.service import UserService


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise HTTPException(status_code=401)
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except ExpiredSignatureError:
        # Как позже выяснилось, ключ exp автоматически проверяется
        # командой jwt.decode, поэтому отдельно проверять это не нужно
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UserService.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user


async def get_curent_admin_user(current_user: User = Depends(get_current_user)):
    # if current_user.role != "admin":
    # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user
