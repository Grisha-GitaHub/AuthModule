from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .base import Base


class RolePermission(Base):
    """Связь ролей и разрешений (какие права есть у роли)"""

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), index=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), index=True)

    # Связи
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", lazy="joined")

    def __repr__(self) -> str:
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"
