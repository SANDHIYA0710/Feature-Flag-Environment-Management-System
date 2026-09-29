from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class EnvironmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None


class EnvironmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = None
    is_active: bool | None = None


class EnvironmentOut(ORMModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
