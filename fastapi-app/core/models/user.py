from sqlalchemy.orm import Mapped, mapped_column
from pydantic import EmailStr

from .base import Base

class User(Base):
    username: Mapped[str] 
    userfamily: Mapped[str]
    userpatronic: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] 