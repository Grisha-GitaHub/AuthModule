from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, func
from datetime import datetime

from .base import Base


class TokenBlacklist(Base):
    """Чёрный список JWT токенов (для реализации logout)"""

    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    blacklisted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<TokenBlacklist token={self.token[:20]}...>"
