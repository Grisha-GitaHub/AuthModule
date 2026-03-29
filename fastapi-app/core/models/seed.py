from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Permission, Role, RolePermission, UserRole


async def create_role(session: AsyncSession, name: str, description: str | None = None) -> Role:
    """Создание роли"""
    role = Role(name=name, description=description)
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


async def create_permission(session: AsyncSession, name: str, description: str | None = None) -> Permission:
    """Создание права"""
    perm = Permission(name=name, description=description)
    session.add(perm)
    await session.commit()
    await session.refresh(perm)
    return perm


async def assign_role_to_user(session: AsyncSession, user_id: int, role_id: int) -> UserRole:
    """Назначение роли пользователю"""
    user_role = UserRole(user_id=user_id, role_id=role_id)
    session.add(user_role)
    await session.commit()
    await session.refresh(user_role)
    return user_role


async def assign_permission_to_role(session: AsyncSession, role_id: int, permission_id: int) -> RolePermission:
    """Назначение права роли"""
    role_perm = RolePermission(role_id=role_id, permission_id=permission_id)
    session.add(role_perm)
    await session.commit()
    await session.refresh(role_perm)
    return role_perm


async def init_db(session: AsyncSession):
    """Инициализация БД тестовыми данными"""
    # Проверка наличия данных
    stmt = select(Role)
    result = await session.execute(stmt)
    if result.scalars().first():
        return  # Данные уже есть

    # Создание прав
    permissions = {
        "create": await create_permission(session, "create", "Создание объектов"),
        "read": await create_permission(session, "read", "Чтение объектов"),
        "update": await create_permission(session, "update", "Обновление объектов"),
        "delete": await create_permission(session, "delete", "Удаление объектов"),
    }

    # Создание ролей
    roles = {
        "admin": await create_role(session, "admin", "Администратор - полный доступ"),
        "manager": await create_role(session, "manager", "Менеджер - чтение и обновление"),
        "user": await create_role(session, "user", "Пользователь - только чтение"),
    }

    # Назначение прав ролям
    # Admin - все права
    for perm in permissions.values():
        await assign_permission_to_role(session, roles["admin"].id, perm.id)

    # Manager - чтение и обновление
    await assign_permission_to_role(session, roles["manager"].id, permissions["read"].id)
    await assign_permission_to_role(session, roles["manager"].id, permissions["update"].id)

    # User - только чтение
    await assign_permission_to_role(session, roles["user"].id, permissions["read"].id)

    await session.commit()


async def get_or_create_role(session: AsyncSession, name: str, description: str | None = None) -> Role:
    """Получение или создание роли"""
    stmt = select(Role).where(Role.name == name)
    result = await session.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        role = await create_role(session, name, description)
    return role


async def get_or_create_permission(session: AsyncSession, name: str, description: str | None = None) -> Permission:
    """Получение или создание права"""
    stmt = select(Permission).where(Permission.name == name)
    result = await session.execute(stmt)
    perm = result.scalar_one_or_none()
    if not perm:
        perm = await create_permission(session, name, description)
    return perm
