from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.jwt_auth import create_access_token, get_current_user
from core.config import settings
from core.models import User
from core.models.db_helper import db_helper

router = APIRouter(tags=["Токены"])


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """Выход из системы с удалением cookie"""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Вы успешно вышли из системы"}


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Обновить access токен"""
    token = create_access_token(
        data={"sub": str(current_user.id), "username": current_user.username, "email": current_user.email}
    )

    return {
        "access_token": token,
        "token_type": settings.auth_JWT.TOKEN_TYPE,
        "email": current_user.email
    }
