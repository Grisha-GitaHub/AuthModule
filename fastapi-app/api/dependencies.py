from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, user_has_permission, get_user_permissions, get_user_roles
from core.models.db_helper import db_helper
from api.auth.jwt_auth import get_current_user as base_get_current_user


def require_permission(permission_name: str):
    """Dependency для проверки наличия права у пользователя"""
    async def permission_checker(
        current_user: User = Depends(base_get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session)
    ) -> User:
        has_permission = await user_has_permission(
            session,
            current_user.id,
            permission_name,
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав для доступа. Требуется право: {permission_name}"
            )
        return current_user
    return permission_checker


def require_role(role_name: str):
    """Dependency для проверки наличия роли у пользователя"""
    async def role_checker(
        current_user: User = Depends(base_get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session)
    ) -> User:
        roles = await get_user_roles(session, current_user.id)
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль: {role_name}. Ваши роли: {', '.join(roles) if roles else 'нет ролей'}"
            )
        return current_user
    return role_checker


async def get_current_user_with_permissions(
    current_user: User = Depends(base_get_current_user),
    session: AsyncSession = Depends(db_helper.get_scoped_session)
) -> dict:
    """Получение текущего пользователя с его правами и ролями"""
    permissions = await get_user_permissions(session, current_user.id)
    roles = await get_user_roles(session, current_user.id)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "roles": roles,
        "permissions": permissions
    }
