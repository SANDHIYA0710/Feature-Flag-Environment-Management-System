from app.db.database import SessionLocal
from app.models import (
    Role,
    User,
    Environment,
    FeatureFlag,
    FeatureRollout,
    UserAssignment,
    AuditLog,
)
from app.core.security import hash_password

def seed():
    db = SessionLocal()
    try:
        roles = [
            ("admin", "Full platform administration"),
            ("developer", "Feature and rollout management"),
            ("viewer", "Read-only access"),
        ]
        role_map = {}
        for name, description in roles:
            role = db.query(Role).filter_by(name=name).first()
            if not role:
                role = Role(name=name, description=description); db.add(role); db.flush()
            role_map[name] = role
        admin = db.query(User).filter_by(email="admin@example.com").first()
        if not admin:
            admin = User(email="admin@example.com", full_name="System Admin", password_hash=hash_password("Admin@123"), role_id=role_map["admin"].id)
            db.add(admin); db.flush()
        for name, description in [("development", "Developer environment"), ("testing", "QA and testing environment"), ("production", "Customer-facing production environment")]:
            if not db.query(Environment).filter_by(name=name).first(): db.add(Environment(name=name, description=description))
        if not db.query(FeatureFlag).filter_by(key="new_payment_ui").first():
            db.add(FeatureFlag(name="New Payment UI", key="new_payment_ui", description="Gradual release example feature", default_enabled=False, created_by=admin.id))
        db.commit()
        print("Seed complete. Admin: admin@example.com / Admin@123")
    finally:
        db.close()

if __name__ == "__main__": seed()
