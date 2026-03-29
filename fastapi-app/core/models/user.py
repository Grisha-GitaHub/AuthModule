from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String

from .base import Base


class User(Base):
    username: Mapped[str] = mapped_column(String(50))
    userfamily: Mapped[str] = mapped_column(String(50))
    userpatronic: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[bytes] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Связи
    roles = relationship("UserRole", back_populates="user", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"  
