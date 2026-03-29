from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func
from datetime import datetime

from .base import Base


class UserRole(Base):
    """Связь пользователей и ролей (многие-ко-многим)"""

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), index=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Связи
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

    def __repr__(self) -> str:
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
