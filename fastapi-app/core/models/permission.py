from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base


class Permission(Base):
    """Разрешение на выполнение действия"""

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Связи
    roles = relationship("RolePermission", back_populates="permission", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"
