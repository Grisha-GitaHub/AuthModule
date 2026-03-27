from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CreateUser
from api.users import crud
from core.models.db_helper import db_helper
from api.auth import jwt_auth

router = APIRouter(tags=["Пользователи"])

@router.post("/register")
async def create_user(
    user: CreateUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):  
    try:
        if CreateUser.password == CreateUser.check_password:    
            return await crud.create_user(session=session, user_in=user)
    except:
        HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Не совпадение паролей")
        

@router.patch("/update_me")
async def update_user_profile(
    user_update: dict,
    sesion: AsyncSession = Depends(db_helper.get_scoped_session),
    current_user = Depends(jwt_auth.get_current_user)
):
    if "username" and "userfamily" and "userpatronic" and "password" not in user_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно заполнить хотя бы одно поле"
            
        )
    