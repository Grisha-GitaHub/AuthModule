from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Permission, Role, RolePermission, UserRole


async def get_role_by_name(session: AsyncSession, name: str) -> Role | None:
    """Получение роли по имени"""
    stmt = select(Role).where(Role.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_permission_by_name(session: AsyncSession, name: str) -> Permission | None:
    """Получение права по имени"""
    stmt = select(Permission).where(Permission.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_role_ids(session: AsyncSession, user_id: int) -> list[int]:
    """Получение ID ролей пользователя"""
    stmt = select(UserRole.role_id).where(UserRole.user_id == user_id)
    result = await session.execute(stmt)
    return [r[0] for r in result.all()]


async def get_role_permission_ids(session: AsyncSession, role_id: int) -> list[int]:
    """Получение ID прав роли"""
    stmt = select(RolePermission.permission_id).where(RolePermission.role_id == role_id)
    result = await session.execute(stmt)
    return [r[0] for r in result.all()]


async def user_has_permission(
    session: AsyncSession,
    user_id: int,
    permission_name: str,
) -> bool:
    """Проверка наличия права у пользователя"""
    permission = await get_permission_by_name(session, permission_name)
    if not permission:
        return False

    user_role_ids = await get_user_role_ids(session, user_id)
    if not user_role_ids:
        return False

    for role_id in user_role_ids:
        role_permission_ids = await get_role_permission_ids(session, role_id)
        if permission.id in role_permission_ids:
            return True

    return False


async def get_user_permissions(session: AsyncSession, user_id: int) -> list[str]:
    """Получение всех прав пользователя"""
    user_role_ids = await get_user_role_ids(session, user_id)
    if not user_role_ids:
        return []

    permissions = set()
    for role_id in user_role_ids:
        role_permission_ids = await get_role_permission_ids(session, role_id)
        for perm_id in role_permission_ids:
            perm = await session.get(Permission, perm_id)
            if perm:
                permissions.add(perm.name)

    return list(permissions)


async def get_user_roles(session: AsyncSession, user_id: int) -> list[str]:
    """Получение всех ролей пользователя"""
    user_role_ids = await get_user_role_ids(session, user_id)
    if not user_role_ids:
        return []

    roles = []
    for role_id in user_role_ids:
        role = await session.get(Role, role_id)
        if role:
            roles.append(role.name)

    return roles
