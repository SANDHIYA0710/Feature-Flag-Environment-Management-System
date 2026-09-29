from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import ORMModel


class RoleOut(ORMModel):
    id: int
    name: str
    description: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6)
    role_id: int = 3


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    role_id: int | None = None
    is_active: bool | None = None


class UserOut(ORMModel):
    id: int
    email: EmailStr
    full_name: str
    role_id: int
    role: RoleOut
    is_active: bool
    created_at: datetime
