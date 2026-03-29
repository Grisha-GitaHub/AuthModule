from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import require_role
from core.models import Permission, Role, User
from core.models.access_control import get_user_roles
from core.models.db_helper import db_helper
from core.models.seed import (
    assign_permission_to_role,
    assign_role_to_user,
    create_permission,
    create_role,
)

router = APIRouter(tags=["Администрирование"], dependencies=[Depends(require_role("admin"))])


# === Роли ===


@router.get("/roles")
async def get_roles(session: AsyncSession = Depends(db_helper.get_scoped_session)):
    """Получить все роли"""
    stmt = select(Role).order_by(Role.id)
    result = await session.execute(stmt)
    roles = result.scalars().all()
    return [{"id": r.id, "name": r.name, "description": r.description} for r in roles]


@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    name: str,
    description: str | None = None,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Создать новую роль"""
    stmt = select(Role).where(Role.name == name)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Роль уже существует")

    role = await create_role(session, name, description)
    return {"id": role.id, "name": role.name, "description": role.description}


# === Права ===


@router.get("/permissions")
async def get_permissions(session: AsyncSession = Depends(db_helper.get_scoped_session)):
    """Получить все права"""
    stmt = select(Permission).order_by(Permission.id)
    result = await session.execute(stmt)
    perms = result.scalars().all()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in perms]


@router.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission_endpoint(
    name: str,
    description: str | None = None,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Создать новое право"""
    stmt = select(Permission).where(Permission.name == name)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Право уже существует")

    perm = await create_permission(session, name, description)
    return {"id": perm.id, "name": perm.name, "description": perm.description}


# === Назначение прав ролям ===


@router.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role_endpoint(
    role_id: int,
    permission_id: int,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Назначить право роли"""
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    perm = await session.get(Permission, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Право не найдено")

    await assign_permission_to_role(session, role_id, permission_id)
    return {"message": f"Право '{perm.name}' назначено роли '{role.name}'"}


# === Назначение ролей пользователям ===


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user_endpoint(
    user_id: int,
    role_id: int,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Назначить роль пользователю"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    await assign_role_to_user(session, user_id, role_id)
    return {"message": f"Роль '{role.name}' назначена пользователю '{user.email}'"}


@router.get("/users/{user_id}/roles")
async def get_user_roles_endpoint(
    user_id: int,
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Получить роли пользователя"""
    roles = await get_user_roles(session, user_id)
    return {"user_id": user_id, "roles": roles}
