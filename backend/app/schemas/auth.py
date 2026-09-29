from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6)


class UserMe(ORMModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
