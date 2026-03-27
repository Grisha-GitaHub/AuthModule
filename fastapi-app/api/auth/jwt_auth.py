
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone

from api.users.schemas import UserSchema
from api.auth import utils as auth_utlis

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.models.db_helper import db_helper

from api.users.schemas import CreateUser, LoginUser
from api.users import crud
from core.config import settings

router = APIRouter(tags=["Авторизация"])

http_bearer = HTTPBearer()

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return auth_utlis.encode_jwt(payload)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(db_helper.get_scoped_session)
) -> User:
    try:
        payload: str = auth_utlis.decoded_jwt(token.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не валиден")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не валиден")
    
    user = await crud.get_user(session, user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    
    return user

@router.post("/login")
async def login(
    user_in: LoginUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session)  
):
    user = await crud.get_user_by_email(session, user_in.email)
    
    if not user or not auth_utlis.validate_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    
    token = create_access_token(data={"sub": str(user.id), "username": user.username, "email": user.email})
    
    return {
        "access_token": token,
        "token_type": settings.auth_JWT.TOKEN_TYPE,
        "email": user.email
    }
    
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return{
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

