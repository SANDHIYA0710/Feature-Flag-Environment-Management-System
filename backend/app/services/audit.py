from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def record_audit(db: Session, user_id: int | None, action: str, entity_type: str, entity_id: str | None = None,
                 feature_flag_id: int | None = None, old_value: dict | None = None, new_value: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id,
                    feature_flag_id=feature_flag_id, old_value=old_value, new_value=new_value))
