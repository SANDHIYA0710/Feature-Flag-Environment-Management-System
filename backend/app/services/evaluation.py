import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.feature import FeatureFlag, FeatureRollout, UserAssignment, Environment


def deterministic_bucket(user_id: int, feature_key: str) -> Decimal:
    digest = hashlib.sha256(f"{feature_key}:{user_id}".encode()).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF * 100
    return Decimal(str(round(value, 2)))


def evaluate_feature(db: Session, feature_key: str, environment_name: str, user_id: int | None = None):
    flag = db.query(FeatureFlag).filter(FeatureFlag.key == feature_key, FeatureFlag.is_archived.is_(False)).first()
    if not flag:
        return False, "feature_not_found", Decimal("0.00")
    env = db.query(Environment).filter(Environment.name == environment_name, Environment.is_active.is_(True)).first()
    if not env:
        return False, "environment_not_found", Decimal("0.00")
    if user_id is not None:
        assignment = db.query(UserAssignment).filter(UserAssignment.feature_flag_id == flag.id, UserAssignment.user_id == user_id).first()
        if assignment:
            return assignment.enabled, "user_assignment", Decimal("100.00")
    rollout = db.query(FeatureRollout).filter(FeatureRollout.feature_flag_id == flag.id, FeatureRollout.environment_id == env.id).first()
    if not rollout:
        return flag.default_enabled, "feature_default", Decimal("100.00" if flag.default_enabled else "0.00")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if rollout.start_at and now < rollout.start_at:
        return False, "scheduled_not_started", rollout.percentage
    if rollout.end_at and now >= rollout.end_at:
        return False, "scheduled_expired", rollout.percentage
    if not rollout.enabled:
        return False, "rollout_disabled", rollout.percentage
    if rollout.percentage >= 100:
        return True, "rollout_100_percent", rollout.percentage
    if rollout.percentage <= 0:
        return False, "rollout_0_percent", rollout.percentage
    if user_id is None:
        return True, "percentage_rollout_no_user_context", rollout.percentage
    return deterministic_bucket(user_id, feature_key) < rollout.percentage, "percentage_rollout", rollout.percentage
