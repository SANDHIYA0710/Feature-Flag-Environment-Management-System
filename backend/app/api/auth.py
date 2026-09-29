from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.db.database import get_db
from app.models.user import Role, User
from app.schemas.auth import LoginRequest, RegisterRequest, UserMe
from app.schemas.common import TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.role)).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))


@router.post("/refresh", response_model=TokenResponse, summary="Refresh Token")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        user_id = decode_token(refresh_token, "refresh")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))


@router.get("/me", response_model=UserMe, summary="Read Current User")
def me(current_user: User = Depends(get_current_user)):
    return UserMe(id=current_user.id, email=current_user.email, full_name=current_user.full_name,
                  role=current_user.role.name, is_active=current_user.is_active)


@router.post("/register", response_model=UserMe, summary="Self Register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    role = db.query(Role).filter(Role.name == "viewer").first()
    user = User(email=payload.email, full_name=payload.full_name, password_hash=hash_password(payload.password), role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserMe(id=user.id, email=user.email, full_name=user.full_name, role=role.name, is_active=user.is_active)
