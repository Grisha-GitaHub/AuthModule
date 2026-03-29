
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import utils as auth_utils
from api.users import crud
from api.users.schemas import LoginUser
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

router = APIRouter(tags=["Авторизация"])


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return auth_utils.encode_jwt(payload)


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
) -> User:
    """Получение текущего пользователя из токена (Header или Cookie)"""
    token = None
    
    # Сначала пробуем получить токен из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    # Если нет в заголовке, пробуем получить из cookie
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен. Используйте заголовок Authorization или cookie."
        )
    
    try:
        payload: dict = auth_utils.decoded_jwt(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не валиден")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не валиден")

    user = await crud.get_user(session, user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт деактивирован")

    return user


@router.post("/login")
async def login(
    response: Response,
    user_in: LoginUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    user = await crud.get_user_by_email(session, user_in.email)

    if not user or not auth_utils.validate_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт деактивирован")

    token = create_access_token(data={"sub": str(user.id), "username": user.username, "email": user.email})

    # Очищаем старые cookie перед установкой новых (защита от переключения пользователей)
    response.delete_cookie(key="access_token", path="/")

    # Устанавливаем токен в httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.auth_JWT.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # в секундах
        httponly=True,  # недоступно для JavaScript
        secure=False,  # True только для HTTPS
        samesite="lax",  # защита от CSRF
        path="/"
    )

    return {
        "access_token": token,
        "token_type": settings.auth_JWT.TOKEN_TYPE,
        "email": user.email,
        "message": "Токен также установлен в cookie"
    }


@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    """Выход из системы с удалением cookie"""
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    return {"message": "Вы успешно вышли из системы"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

  
