from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base


class Role(Base):
    """Роль пользователя в системе"""

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Связи
    users = relationship("UserRole", back_populates="role", lazy="selectin")
    permissions = relationship("RolePermission", back_populates="role", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"
