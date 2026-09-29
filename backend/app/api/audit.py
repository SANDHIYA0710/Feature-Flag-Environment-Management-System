from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogOut

router = APIRouter(prefix="/api/v1/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogOut], summary="List Audit Logs")
def list_audit_logs(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
