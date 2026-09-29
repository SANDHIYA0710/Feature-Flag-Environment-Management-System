from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.database import get_db
from app.models.feature import UserAssignment
from app.models.user import User
from app.redis.client import cache_delete
from app.schemas.feature import AssignmentCreate, AssignmentOut
from app.services.audit import record_audit
from app.api.features import feature_or_404

router = APIRouter(prefix="/api/v1/feature-flags", tags=["User Targeting"])


@router.get("/{flag_id}/assignments", response_model=list[AssignmentOut], summary="List Assignments")
def list_assignments(flag_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    feature_or_404(db, flag_id)
    return db.query(UserAssignment).filter_by(feature_flag_id=flag_id).order_by(UserAssignment.id.desc()).all()


@router.post("/{flag_id}/assignments", response_model=AssignmentOut, summary="Create Assignment")
def create_assignment(
    flag_id: int,
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles("admin", "developer")),
):
    flag = feature_or_404(db, flag_id)
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")

    assignment = db.query(UserAssignment).filter_by(
        feature_flag_id=flag_id,
        user_id=payload.user_id,
    ).first()

    if assignment:
        assignment.enabled = payload.enabled
        assignment.reason = payload.reason
    else:
        assignment = UserAssignment(
            feature_flag_id=flag_id,
            **payload.model_dump(),
        )
        db.add(assignment)

    db.flush()
    record_audit(
        db,
        current.id,
        "USER_ASSIGNMENT_UPDATED",
        "user_assignment",
        str(assignment.id),
        flag.id,
        new_value=payload.model_dump(),
    )
    cache_delete(f"flag_eval:{flag.key}:*")
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{flag_id}/assignments/{assignment_id}", summary="Delete Assignment")
def delete_assignment(
    flag_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles("admin", "developer")),
):
    flag = feature_or_404(db, flag_id)
    assignment = db.query(UserAssignment).filter_by(
        id=assignment_id,
        feature_flag_id=flag_id,
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    record_audit(
        db,
        current.id,
        "USER_ASSIGNMENT_DELETED",
        "user_assignment",
        str(assignment_id),
        flag.id,
    )
    cache_delete(f"flag_eval:{flag.key}:*")
    db.commit()
    return {"message": "Assignment deleted"}
