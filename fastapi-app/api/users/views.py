from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import jwt_auth
from api.users import crud
from api.users.schemas import CreateUser, UpdateUser, UserSchema
from core.models import User
from core.models.db_helper import db_helper

router = APIRouter(tags=["Пользователи"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: CreateUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    if user_in.password != user_in.check_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароли не совпадают"
        )
    
    existing_user = await crud.get_user_by_email(session, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )
    
    return await crud.create_user(session=session, user_in=user_in)


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(jwt_auth.get_current_user)
):
    return current_user


@router.patch("/update_me", response_model=UserSchema)
async def update_user_profile(
    user_update: UpdateUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session),
    current_user: User = Depends(jwt_auth.get_current_user)
):
    update_data = user_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно заполнить хотя бы одно поле"
        )
    
    return await crud.update_user(session=session, user=current_user, update_data=update_data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    session: AsyncSession = Depends(db_helper.get_scoped_session),
    current_user: User = Depends(jwt_auth.get_current_user)
):
    await crud.soft_delete_user(session=session, user=current_user)
      
