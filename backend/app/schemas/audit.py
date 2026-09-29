from datetime import datetime
from app.schemas.common import ORMModel


class AuditLogOut(ORMModel):
    id: int
    user_id: int | None
    feature_flag_id: int | None
    action: str
    entity_type: str
    entity_id: str | None
    old_value: dict | None
    new_value: dict | None
    created_at: datetime
