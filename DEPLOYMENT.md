# Atai Travel Deployment Guide

This guide deploys Atai Travel for a hackathon demo with:

- Backend: Railway
- Database: Railway PostgreSQL
- Frontend: Vercel
- Auth: HTTP-only cookie
- AI assistant: https://think-with-me-bot.lovable.app

## 1. Backend On Railway

### Create Railway Project

1. Push this repository to GitHub.
2. Open Railway and create a new project.
3. Add a PostgreSQL service.
4. Add a backend service from the GitHub repository.
5. Set the backend root directory to:

```text
backend
```

### Railway Build / Install Command

```bash
pip install -r requirements.txt
```

### Railway Start Command

```bash
python -m alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Railway Environment Variables

Set these variables in the Railway backend service:

```env
SECRET_KEY=<64-char-random-hex>
DATABASE_URL=<Railway PostgreSQL connection URL>
ENVIRONMENT=production
FRONTEND_URL=https://YOUR_VERCEL_URL
COOKIE_SECURE=true
COOKIE_SAMESITE=none
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Generate a secret key locally:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Railway usually provides a PostgreSQL URL in the right format. If your provider gives a URL starting with `postgres://`, convert it to `postgresql://` or `postgresql+psycopg2://`.

## 2. Frontend On Vercel

1. Import the GitHub repository into Vercel.
2. Set the frontend root directory to:

```text
frontend
```

3. Set build command:

```bash
npm run build
```

4. Set output directory:

```text
dist
```

### Vercel Environment Variables

```env
VITE_API_URL=https://YOUR_RAILWAY_BACKEND_URL
VITE_AI_ASSISTANT_URL=https://think-with-me-bot.lovable.app
```

After setting env variables, redeploy the frontend.

## 3. Cookie Login Checklist

Because frontend and backend are on different domains during the hackathon, login depends on these settings:

Backend Railway:

```env
COOKIE_SECURE=true
COOKIE_SAMESITE=none
FRONTEND_URL=https://YOUR_VERCEL_URL
```

Frontend Vercel:

```env
VITE_API_URL=https://YOUR_RAILWAY_BACKEND_URL
```

The backend must be HTTPS. Railway and Vercel provide HTTPS by default.

## 4. Local Development

Backend:

```bash
cd backend
pip install -r requirements.txt
python -m alembic upgrade head
python seed.py
python -m uvicorn app.main:app --reload --port 8001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Local URLs:

```text
Frontend: http://localhost:5173
Backend:  http://127.0.0.1:8001
Docs:     http://127.0.0.1:8001/docs
```

## 5. Verification Commands

Backend:

```bash
cd backend
python -m pytest tests/ -v
```

Frontend:

```bash
cd frontend
npm run build
```

On Windows PowerShell, use this if needed:

```bash
npm.cmd run build
```

## 6. Manual Online Test

1. Open the Vercel frontend URL.
2. Register a new user.
3. Log in.
4. Refresh the page and confirm the session stays active.
5. Open `/packages`.
6. Open `/ai-assistant`.
7. Create a travel request.
8. Log in as a partner.
9. Open `/partner/requests`.
10. Send an offer.

## 7. Hackathon Risks

- Cross-domain cookie auth must be tested first.
- Railway PostgreSQL starts empty, so Alembic must run successfully during deploy.
- Demo data is not automatically seeded in production unless you run `python seed.py` manually or add a controlled seed step.
- Some MVP business rules still need production hardening after the demo, especially booking inventory and pagination.
