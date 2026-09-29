"""initial schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("roles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False, unique=True), sa.Column("description", sa.String(255)), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("environments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False, unique=True), sa.Column("description", sa.String(255)), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("feature_flags", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("key", sa.String(120), nullable=False, unique=True), sa.Column("description", sa.Text()), sa.Column("default_enabled", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("feature_rollouts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("feature_flag_id", sa.Integer(), sa.ForeignKey("feature_flags.id", ondelete="CASCADE"), nullable=False), sa.Column("environment_id", sa.Integer(), sa.ForeignKey("environments.id", ondelete="CASCADE"), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("percentage", sa.Numeric(5,2), nullable=False, server_default="0"), sa.Column("start_at", sa.DateTime()), sa.Column("end_at", sa.DateTime()), sa.Column("previous_enabled", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("previous_percentage", sa.Numeric(5,2), nullable=False, server_default="0"), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.UniqueConstraint("feature_flag_id", "environment_id", name="uq_feature_environment"))
    op.create_table("user_assignments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("feature_flag_id", sa.Integer(), sa.ForeignKey("feature_flags.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("reason", sa.String(255)), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.UniqueConstraint("feature_flag_id", "user_id", name="uq_feature_user"))
    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("feature_flag_id", sa.Integer(), sa.ForeignKey("feature_flags.id", ondelete="SET NULL")), sa.Column("action", sa.String(80), nullable=False), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", sa.String(80)), sa.Column("old_value", sa.JSON()), sa.Column("new_value", sa.JSON()), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))


def downgrade():
    for table in ["audit_logs", "user_assignments", "feature_rollouts", "feature_flags", "environments", "users", "roles"]:
        op.drop_table(table)
