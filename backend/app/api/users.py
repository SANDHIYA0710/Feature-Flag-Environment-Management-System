from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.dependencies import get_current_user, require_roles
from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import Role, User
from app.schemas.user import RoleOut, UserCreate, UserOut, UserUpdate
from app.services.audit import record_audit

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("", response_model=list[UserOut], summary="List Users")
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(User).options(joinedload(User.role)).order_by(User.id.desc()).all()


@router.post("", response_model=UserOut, summary="Create User")
def create_user(payload: UserCreate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    if not db.get(Role, payload.role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    user = User(email=payload.email, full_name=payload.full_name, password_hash=hash_password(payload.password), role_id=payload.role_id)
    db.add(user)
    db.flush()
    record_audit(db, current.id, "USER_CREATED", "user", str(user.id), new_value={"email": user.email, "role_id": user.role_id})
    db.commit()
    return db.query(User).options(joinedload(User.role)).get(user.id)


@router.get("/roles", response_model=list[RoleOut], summary="List Roles")
def list_roles(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Role).order_by(Role.id).all()


@router.patch("/{user_id}", response_model=UserOut, summary="Update User")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    user = db.query(User).options(joinedload(User.role)).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old = {"full_name": user.full_name, "role_id": user.role_id, "is_active": user.is_active}
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    if payload.role_id is not None and not db.get(Role, payload.role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    record_audit(db, current.id, "USER_UPDATED", "user", str(user.id), old_value=old, new_value=payload.model_dump(exclude_unset=True))
    db.commit()
    return db.query(User).options(joinedload(User.role)).get(user.id)


@router.delete("/{user_id}", summary="Delete User")
def delete_user(user_id: int, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    db.delete(user)
    record_audit(db, current.id, "USER_DELETED", "user", str(user_id))
    db.commit()
    return {"message": "User deleted"}
