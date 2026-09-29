from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    rollouts: Mapped[list["FeatureRollout"]] = relationship(back_populates="environment", cascade="all, delete-orphan")


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    rollouts: Mapped[list["FeatureRollout"]] = relationship(back_populates="feature_flag", cascade="all, delete-orphan")
    assignments: Mapped[list["UserAssignment"]] = relationship(back_populates="feature_flag", cascade="all, delete-orphan")


class FeatureRollout(Base):
    __tablename__ = "feature_rollouts"
    __table_args__ = (UniqueConstraint("feature_flag_id", "environment_id", name="uq_feature_environment"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    feature_flag_id: Mapped[int] = mapped_column(ForeignKey("feature_flags.id"), index=True)
    environment_id: Mapped[int] = mapped_column(ForeignKey("environments.id"), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    start_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    previous_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    previous_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    feature_flag: Mapped[FeatureFlag] = relationship(back_populates="rollouts")
    environment: Mapped[Environment] = relationship(back_populates="rollouts")


class UserAssignment(Base):
    __tablename__ = "user_assignments"
    __table_args__ = (UniqueConstraint("feature_flag_id", "user_id", name="uq_feature_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    feature_flag_id: Mapped[int] = mapped_column(ForeignKey("feature_flags.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    feature_flag: Mapped[FeatureFlag] = relationship(back_populates="assignments")
    user: Mapped["User"] = relationship(back_populates="assignments")
