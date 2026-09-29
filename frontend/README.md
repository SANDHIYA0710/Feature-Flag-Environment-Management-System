# FlagVault Luxury Frontend

Premium React + TypeScript frontend for the Feature Flag & Environment Management System.

## Stack
- React + Vite + TypeScript
- Material UI
- Axios
- Recharts
- Docker + Nginx

## Run locally

```bash
npm install
npm run dev
```

Open http://localhost:5173

## Docker

```bash
docker build -t feature-flag-luxury-frontend .
docker run --rm -p 5173:80 feature-flag-luxury-frontend
```

## API

Default API base:
`http://localhost:8000/api/v1`

Override with:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

The frontend keeps JWT access tokens in localStorage under `access_token` and automatically sends them as Bearer authentication.

## Notes

The UI is designed to preserve the existing FastAPI endpoint contract:
- `/auth/login`
- `/feature-flags`
- `/environments`
- `/feature-flags/{id}/rollouts/{env_id}`
- `/feature-flags/{id}/assignments`
- `/evaluate`
- `/audit-logs`
- `/dashboard/summary`
- `/dashboard/top-flags`
- `/dashboard/analytics/{id}`

If your backend request schema has additional required fields for an operation, add them to the corresponding form in `src/App.tsx`.
