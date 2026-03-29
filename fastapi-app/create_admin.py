"""
Скрипт для создания пользователя admin с id=1 и назначения роли администратора
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

from api.auth.utils import hash_password
from core.models import Role, User, UserRole
from core.models.db_helper import db_helper

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))


async def create_admin():
    async with db_helper.session_factory() as session:
        user = await session.get(User, 1)

        if not user:
            print("User with id=1 not found, creating...")

            stmt = select(User).where(User.email == "admin@admin.com")
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                print(f"Found existing user: {user.email} (id={user.id})")
            else:
                hashed_password = hash_password("admin123")
                user = User(
                    username="Admin",
                    userfamily="Admin",
                    userpatronic="Admin",
                    email="admin@admin.com",
                    hashed_password=hashed_password,
                    is_active=True,
                )
                session.add(user)
                await session.flush()
                print(f"Created user: {user.email} (id={user.id})")

        stmt = select(Role).where(Role.name == "admin")
        result = await session.execute(stmt)
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            print("ERROR: Role 'admin' not found")
            return

        stmt = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == admin_role.id,
        )
        result = await session.execute(stmt)
        existing_role = result.scalar_one_or_none()

        if existing_role:
            print("WARNING: User already has role 'admin'")
        else:
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            session.add(user_role)
            await session.commit()
            print(f"SUCCESS: User {user.email} assigned role 'admin'")

        print("\n=== Login Credentials ===")
        print("Email: admin@admin.com")
        print("Password: admin123")


if __name__ == "__main__":
    asyncio.run(create_admin())
