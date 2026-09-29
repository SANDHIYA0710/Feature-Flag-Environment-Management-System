# Feature Flag & Environment Management System

A production-style full-stack platform for controlling application features without redeployment.

## Objective
Administrators and authorized users can create and manage feature flags, control them per environment, gradually roll them out by percentage, target individual users, schedule activation windows, evaluate flags at runtime, review audit history, and rollback rollout changes.

## Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, JWT, Redis
- Frontend: React + Vite, TypeScript, Material UI, Axios, React Router, Chart.js
- Database: MySQL 8.0
- Infrastructure: Docker Compose
- API testing: Swagger UI + Postman collection

## Modules
1. JWT login / refresh / current user / self-registration
2. Role-based access control: admin, developer, viewer
3. User and role administration
4. Feature flag CRUD
5. Development / Testing / Production environment management
6. Percentage-based rollout using deterministic user bucketing
7. User-specific targeting overrides
8. Scheduled rollout start/end windows
9. Runtime evaluation endpoint
10. Redis integration for cache invalidation and future evaluation caching
11. Audit logs and change history
12. Rollback to the previous rollout state
13. Dashboard and usage analytics

## Exact Swagger endpoints
Open `http://localhost:8000/docs` after startup.

### Authentication
- POST `/api/v1/auth/login`
- POST `/api/v1/auth/refresh`
- GET `/api/v1/auth/me`
- POST `/api/v1/auth/register`

### Users
- GET `/api/v1/users`
- POST `/api/v1/users`
- GET `/api/v1/users/roles`
- PATCH `/api/v1/users/{user_id}`
- DELETE `/api/v1/users/{user_id}`

### Environments
- GET `/api/v1/environments`
- POST `/api/v1/environments`
- PATCH `/api/v1/environments/{env_id}`
- DELETE `/api/v1/environments/{env_id}`

### Feature Flags
- GET `/api/v1/feature-flags`
- POST `/api/v1/feature-flags`
- GET `/api/v1/feature-flags/{flag_id}`
- PATCH `/api/v1/feature-flags/{flag_id}`
- DELETE `/api/v1/feature-flags/{flag_id}`
- GET `/api/v1/feature-flags/{flag_id}/rollouts/{env_id}`
- PUT `/api/v1/feature-flags/{flag_id}/rollouts/{env_id}`
- POST `/api/v1/feature-flags/{flag_id}/rollouts/{env_id}/rollback`

### User Targeting
- GET `/api/v1/feature-flags/{flag_id}/assignments`
- POST `/api/v1/feature-flags/{flag_id}/assignments`
- DELETE `/api/v1/feature-flags/{flag_id}/assignments/{assignment_id}`

### Evaluation
- POST `/api/v1/evaluate`

### Audit Logs
- GET `/api/v1/audit-logs`

### Dashboard & Analytics
- GET `/api/v1/dashboard/summary`
- GET `/api/v1/dashboard/top-flags`
- GET `/api/v1/dashboard/analytics/{flag_id}`

### Health
- GET `/`
- GET `/health`

## Run with Docker
1. Copy `backend/.env.example` to `backend/.env`.
2. From the project root:

```bash
docker compose up --build -d
```

3. Open:
- Frontend: http://localhost:5173
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

The backend automatically runs Alembic migrations and the seed script.

## Demo login
- Email: `admin@example.com`
- Password: `Admin@123`

Change the demo password before using outside a local development environment.

## Database
MySQL is exposed on port `3306`.

```bash
docker compose exec mysql mysql -u feature_user -p feature_flags
```
Password: `feature_password`

Useful SQL:

```sql
SHOW TABLES;
SELECT * FROM users;
SELECT * FROM feature_flags;
SELECT * FROM environments;
SELECT * FROM feature_rollouts;
SELECT * FROM user_assignments;
SELECT * FROM audit_logs;
```

## Local backend without Docker
Use Python 3.12, create a virtual environment, install `backend/requirements.txt`, set `DATABASE_URL` and `REDIS_URL`, run Alembic, seed, then start Uvicorn:

```bash
cd backend
python -m venv venv
# Windows PowerShell
venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

## Feature evaluation logic
Evaluation order:
1. User-specific assignment, if present.
2. Environment rollout, if configured.
3. Scheduled start/end window.
4. Enabled state.
5. Percentage rollout using a deterministic SHA-256 user bucket.
6. Feature default when no environment rollout exists.

This makes a 10% rollout stable for a given user rather than randomly changing on every request.

## Project structure
```text
feature-flag-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── redis/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── scripts/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── types/
│   ├── Dockerfile
│   └── package.json
├── postman/
├── docker-compose.yml
└── README.md
```
