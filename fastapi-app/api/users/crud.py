from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import utils as pswd_utils
from core.models import Role, User, UserRole

from .schemas import CreateUser


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_in: CreateUser) -> User:
    data = user_in.model_dump()
    password = data.pop("password")
    data.pop("check_password", None)
    hashed_password = pswd_utils.hash_password(password)
    data["hashed_password"] = hashed_password
    data["is_active"] = True
    user = User(**data)
    session.add(user)
    await session.flush()  # Получаем ID пользователя

    # Назначаем роль admin первому пользователю
    stmt = select(Role).where(Role.name == "admin")
    result = await session.execute(stmt)
    admin_role = result.scalar_one_or_none()

    if admin_role:
        # Проверяем, есть ли уже пользователи с ролью admin
        stmt = select(UserRole).where(UserRole.role_id == admin_role.id)
        result = await session.execute(stmt)
        existing_admins = result.scalars().all()

        # Если admin нет, назначаем первому пользователю
        if not existing_admins:
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            session.add(user_role)
        else:
            # Иначе назначаем роль user
            stmt = select(Role).where(Role.name == "user")
            result = await session.execute(stmt)
            user_role_obj = result.scalar_one_or_none()
            if user_role_obj:
                user_role = UserRole(user_id=user.id, role_id=user_role_obj.id)
                session.add(user_role)

    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    user: User,
    update_data: dict
) -> User:
    for key, value in update_data.items():
        if key == "password" and value:
            value = pswd_utils.hash_password(value)
            key = "hashed_password"
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user


async def soft_delete_user(session: AsyncSession, user: User) -> User:
    user.is_active = False
    await session.commit()
    await session.refresh(user)
    return user  
