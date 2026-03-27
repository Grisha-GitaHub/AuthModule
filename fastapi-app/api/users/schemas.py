from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUser(BaseModel):
    username: str
    password: str | bytes
    check_password: str | bytes
    email: EmailStr
    
class LoginUser(BaseModel):
    email: EmailStr
    password: str | bytes
    
class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    userfamily: str
    userpatronic: str
    hashed_password: str | bytes
    email: EmailStr
    is_active: bool = True