from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from app.schemas.common import ORMModel


class FeatureCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    key: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    description: str | None = None
    default_enabled: bool = False


class FeatureUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    default_enabled: bool | None = None
    is_archived: bool | None = None


class FeatureOut(ORMModel):
    id: int
    name: str
    key: str
    description: str | None
    default_enabled: bool
    is_archived: bool
    created_by: int
    created_at: datetime
    updated_at: datetime


class RolloutUpdate(BaseModel):
    enabled: bool
    percentage: Decimal = Field(ge=0, le=100)
    start_at: datetime | None = None
    end_at: datetime | None = None

    @field_validator("end_at")
    @classmethod
    def validate_dates(cls, v, info):
        start = info.data.get("start_at")
        if v and start and v <= start:
            raise ValueError("end_at must be after start_at")
        return v


class RolloutOut(ORMModel):
    id: int
    feature_flag_id: int
    environment_id: int
    enabled: bool
    percentage: Decimal
    start_at: datetime | None
    end_at: datetime | None
    previous_enabled: bool
    previous_percentage: Decimal
    updated_at: datetime


class AssignmentCreate(BaseModel):
    user_id: int
    enabled: bool = True
    reason: str | None = None


class AssignmentOut(ORMModel):
    id: int
    feature_flag_id: int
    user_id: int
    enabled: bool
    reason: str | None
    created_at: datetime


class EvaluateRequest(BaseModel):
    feature_key: str
    environment: str
    user_id: int | None = None


class EvaluateResponse(BaseModel):
    feature_key: str
    environment: str
    enabled: bool
    reason: str
    percentage: Decimal
