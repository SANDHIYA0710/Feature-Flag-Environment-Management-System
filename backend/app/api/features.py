from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, require_roles
from app.db.database import get_db
from app.models.feature import Environment, FeatureFlag, FeatureRollout
from app.models.user import User
from app.redis.client import cache_delete
from app.schemas.feature import FeatureCreate, FeatureOut, FeatureUpdate, RolloutOut, RolloutUpdate
from app.services.audit import record_audit

router = APIRouter(prefix="/api/v1/feature-flags", tags=["Feature Flags"])


def feature_or_404(db, flag_id):
    flag = db.get(FeatureFlag, flag_id)
    if not flag: raise HTTPException(status_code=404, detail="Feature flag not found")
    return flag


@router.get("", response_model=list[FeatureOut], summary="List Flags")
def list_flags(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(FeatureFlag).order_by(FeatureFlag.id.desc()).all()


@router.post("", response_model=FeatureOut, summary="Create Flag")
def create_flag(payload: FeatureCreate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin", "developer"))):
    if db.query(FeatureFlag).filter(FeatureFlag.key == payload.key).first():
        raise HTTPException(status_code=409, detail="Feature key already exists")
    flag = FeatureFlag(**payload.model_dump(), created_by=current.id)
    db.add(flag); db.flush()
    record_audit(db, current.id, "FEATURE_CREATED", "feature_flag", str(flag.id), flag.id, new_value=payload.model_dump())
    db.commit(); db.refresh(flag)
    return flag


@router.get("/{flag_id}", response_model=FeatureOut, summary="Get Flag")
def get_flag(flag_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return feature_or_404(db, flag_id)


@router.patch("/{flag_id}", response_model=FeatureOut, summary="Update Flag")
def update_flag(flag_id: int, payload: FeatureUpdate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin", "developer"))):
    flag = feature_or_404(db, flag_id)
    old = {"name": flag.name, "description": flag.description, "default_enabled": flag.default_enabled, "is_archived": flag.is_archived}
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(flag, k, v)
    record_audit(db, current.id, "FEATURE_UPDATED", "feature_flag", str(flag.id), flag.id, old_value=old, new_value=payload.model_dump(exclude_unset=True))
    cache_delete(f"flag_eval:{flag.key}:*")
    db.commit(); db.refresh(flag)
    return flag


@router.delete("/{flag_id}", summary="Delete Flag")
def delete_flag(flag_id: int, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    flag = feature_or_404(db, flag_id)
    db.delete(flag)
    record_audit(db, current.id, "FEATURE_DELETED", "feature_flag", str(flag_id), flag_id)
    cache_delete(f"flag_eval:{flag.key}:*")
    db.commit()
    return {"message": "Feature flag deleted"}


@router.get("/{flag_id}/rollouts/{env_id}", response_model=RolloutOut, summary="Get Rollout")
def get_rollout(flag_id: int, env_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    feature_or_404(db, flag_id)
    rollout = db.query(FeatureRollout).filter_by(feature_flag_id=flag_id, environment_id=env_id).first()
    if not rollout: raise HTTPException(status_code=404, detail="Rollout not configured")
    return rollout


@router.put("/{flag_id}/rollouts/{env_id}", response_model=RolloutOut, summary="Update Rollout")
def update_rollout(flag_id: int, env_id: int, payload: RolloutUpdate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin", "developer"))):
    flag = feature_or_404(db, flag_id)
    if not db.get(Environment, env_id): raise HTTPException(status_code=404, detail="Environment not found")
    rollout = db.query(FeatureRollout).filter_by(feature_flag_id=flag_id, environment_id=env_id).first()
    if not rollout:
        rollout = FeatureRollout(feature_flag_id=flag_id, environment_id=env_id)
        db.add(rollout); db.flush()
    old = {"enabled": rollout.enabled, "percentage": float(rollout.percentage), "start_at": rollout.start_at.isoformat() if rollout.start_at else None, "end_at": rollout.end_at.isoformat() if rollout.end_at else None}
    rollout.previous_enabled = rollout.enabled
    rollout.previous_percentage = rollout.percentage
    rollout.enabled = payload.enabled
    rollout.percentage = payload.percentage
    rollout.start_at = payload.start_at.replace(tzinfo=None) if payload.start_at else None
    rollout.end_at = payload.end_at.replace(tzinfo=None) if payload.end_at else None
    new = {"enabled": payload.enabled, "percentage": float(payload.percentage), "start_at": payload.start_at.isoformat() if payload.start_at else None, "end_at": payload.end_at.isoformat() if payload.end_at else None}
    record_audit(db, current.id, "ROLLOUT_UPDATED", "feature_rollout", str(rollout.id), flag.id, old_value=old, new_value=new)
    cache_delete(f"flag_eval:{flag.key}:*")
    db.commit(); db.refresh(rollout)
    return rollout


@router.post("/{flag_id}/rollouts/{env_id}/rollback", response_model=RolloutOut, summary="Rollback Rollout")
def rollback_rollout(flag_id: int, env_id: int, db: Session = Depends(get_db), current: User = Depends(require_roles("admin", "developer"))):
    flag = feature_or_404(db, flag_id)
    rollout = db.query(FeatureRollout).filter_by(feature_flag_id=flag_id, environment_id=env_id).first()
    if not rollout: raise HTTPException(status_code=404, detail="Rollout not configured")
    old = {"enabled": rollout.enabled, "percentage": float(rollout.percentage)}
    rollout.enabled, rollout.percentage = rollout.previous_enabled, rollout.previous_percentage
    rollout.previous_enabled, rollout.previous_percentage = old["enabled"], old["percentage"]
    record_audit(db, current.id, "ROLLOUT_ROLLBACK", "feature_rollout", str(rollout.id), flag.id, old_value=old,
                 new_value={"enabled": rollout.enabled, "percentage": float(rollout.percentage)})
    cache_delete(f"flag_eval:{flag.key}:*")
    db.commit(); db.refresh(rollout)
    return rollout
