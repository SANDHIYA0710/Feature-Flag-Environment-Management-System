from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.feature import EvaluateRequest, EvaluateResponse
from app.services.evaluation import evaluate_feature
from app.services.audit import record_audit
from app.redis.client import redis_client

router = APIRouter(prefix="/api/v1", tags=["Evaluation"])


@router.post("/evaluate", response_model=EvaluateResponse, summary="Evaluate")
def evaluate(payload: EvaluateRequest, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    user_id = payload.user_id if payload.user_id is not None else current.id
    enabled, reason, percentage = evaluate_feature(db, payload.feature_key, payload.environment, user_id)
    try:
        redis_client.incr(f"feature_usage:{payload.feature_key}")
    except Exception:
        pass
    record_audit(db, current.id, "FEATURE_EVALUATED", "feature_flag", payload.feature_key, new_value={"environment": payload.environment, "user_id": user_id, "enabled": enabled, "reason": reason})
    db.commit()
    return EvaluateResponse(feature_key=payload.feature_key, environment=payload.environment, enabled=enabled, reason=reason, percentage=percentage)
