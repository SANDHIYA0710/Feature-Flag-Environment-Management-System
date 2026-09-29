from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit import AuditLog
from app.models.feature import Environment, FeatureFlag, FeatureRollout
from app.models.user import User

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Analytics"])


@router.get("/summary", summary="Dashboard Summary")
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return {
        "total_features": db.query(func.count(FeatureFlag.id)).filter(FeatureFlag.is_archived.is_(False)).scalar() or 0,
        "enabled_features": db.query(func.count(FeatureFlag.id)).filter(FeatureFlag.default_enabled.is_(True), FeatureFlag.is_archived.is_(False)).scalar() or 0,
        "total_environments": db.query(func.count(Environment.id)).filter(Environment.is_active.is_(True)).scalar() or 0,
        "active_rollouts": db.query(func.count(FeatureRollout.id)).filter(FeatureRollout.enabled.is_(True)).scalar() or 0,
        "audit_events": db.query(func.count(AuditLog.id)).scalar() or 0,
    }


@router.get("/top-flags", summary="Top Flags")
def top_flags(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (db.query(AuditLog.feature_flag_id, func.count(AuditLog.id).label("usage"))
            .filter(AuditLog.action == "FEATURE_EVALUATED", AuditLog.feature_flag_id.is_not(None))
            .group_by(AuditLog.feature_flag_id).order_by(func.count(AuditLog.id).desc()).limit(10).all())
    return [{"feature_flag_id": row[0], "usage": row[1]} for row in rows]


@router.get("/analytics/{flag_id}", summary="Flag Analytics")
def flag_analytics(flag_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if not db.get(FeatureFlag, flag_id): raise HTTPException(status_code=404, detail="Feature flag not found")
    total = db.query(func.count(AuditLog.id)).filter(AuditLog.feature_flag_id == flag_id, AuditLog.action == "FEATURE_EVALUATED").scalar() or 0
    enabled = db.query(func.count(AuditLog.id)).filter(AuditLog.feature_flag_id == flag_id, AuditLog.action == "FEATURE_EVALUATED", AuditLog.new_value["enabled"].as_boolean().is_(True)).scalar() or 0
    return {"feature_flag_id": flag_id, "evaluations": total, "enabled_evaluations": enabled, "disabled_evaluations": total - enabled}
