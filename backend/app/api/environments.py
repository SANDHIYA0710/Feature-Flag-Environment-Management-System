from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles, get_current_user
from app.db.database import get_db
from app.models.feature import Environment
from app.models.user import User
from app.schemas.environment import EnvironmentCreate, EnvironmentOut, EnvironmentUpdate
from app.services.audit import record_audit

router = APIRouter(prefix="/api/v1/environments", tags=["Environments"])


@router.get("", response_model=list[EnvironmentOut], summary="List Environments")
def list_environments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Environment).order_by(Environment.id).all()


@router.post("", response_model=EnvironmentOut, summary="Create Environment")
def create_environment(payload: EnvironmentCreate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    name = payload.name.strip().lower()
    if db.query(Environment).filter(Environment.name == name).first():
        raise HTTPException(status_code=409, detail="Environment already exists")
    env = Environment(name=name, description=payload.description)
    db.add(env)
    db.flush()
    record_audit(db, current.id, "ENVIRONMENT_CREATED", "environment", str(env.id), new_value=payload.model_dump())
    db.commit(); db.refresh(env)
    return env


@router.patch("/{env_id}", response_model=EnvironmentOut, summary="Update Environment")
def update_environment(env_id: int, payload: EnvironmentUpdate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    env = db.get(Environment, env_id)
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    old = {"name": env.name, "description": env.description, "is_active": env.is_active}
    data = payload.model_dump(exclude_unset=True)
    if "name" in data: data["name"] = data["name"].strip().lower()
    for k, v in data.items(): setattr(env, k, v)
    record_audit(db, current.id, "ENVIRONMENT_UPDATED", "environment", str(env.id), old_value=old, new_value=data)
    db.commit(); db.refresh(env)
    return env


@router.delete("/{env_id}", summary="Delete Environment")
def delete_environment(env_id: int, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    env = db.get(Environment, env_id)
    if not env: raise HTTPException(status_code=404, detail="Environment not found")
    db.delete(env)
    record_audit(db, current.id, "ENVIRONMENT_DELETED", "environment", str(env_id))
    db.commit()
    return {"message": "Environment deleted"}
