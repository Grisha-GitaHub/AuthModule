from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUser(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    userfamily: str = Field(..., min_length=1, max_length=50)
    userpatronic: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    check_password: str = Field(..., min_length=6)


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    userfamily: str
    userpatronic: str
    email: EmailStr
    is_active: bool = True


class UpdateUser(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=50)
    userfamily: str | None = Field(None, min_length=1, max_length=50)
    userpatronic: str | None = Field(None, min_length=1, max_length=50)
    password: str | None = Field(None, min_length=6)  
