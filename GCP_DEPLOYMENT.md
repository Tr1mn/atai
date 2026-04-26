# Atai Travel GCP Deployment Plan

This plan prepares Atai Travel for a fast hackathon/MVP deployment on Google Cloud Platform without changing core product logic.

## Recommended MVP Architecture

Use this setup:

- Backend: Cloud Run
- Frontend: Firebase Hosting
- Database: Cloud SQL for PostgreSQL
- Container registry: Artifact Registry
- Secrets: Secret Manager
- Optional CI/CD: GitHub Actions

Why this is the best MVP path:

- Cloud Run runs the FastAPI backend as a container and automatically handles HTTPS, scaling, and `$PORT`.
- Firebase Hosting is simple for Vite/React static hosting and supports SPA rewrites.
- Cloud SQL PostgreSQL gives a managed production database.
- Secret Manager keeps `SECRET_KEY` and `DATABASE_URL` out of GitHub and frontend code.
- No Kubernetes/GKE is needed for a hackathon demo.

## Files Added Or Updated

Backend:

- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/app/database.py`
- `backend/requirements.txt`

Frontend:

- `frontend/firebase.json`
- `frontend/.firebaserc.example`
- `frontend/.env.example`

CI/CD templates:

- `.github/workflows/gcp-backend-cloud-run.yml`
- `.github/workflows/gcp-frontend-firebase.yml`

Docs:

- `GCP_DEPLOYMENT.md`

## Production Readiness Notes

The backend already supports:

- env-based `DATABASE_URL`
- env-based `FRONTEND_URL`
- env-based cookie settings
- HTTP-only JWT cookie
- Alembic migrations
- PostgreSQL driver through `psycopg2-binary`
- Cloud Run `$PORT` through Docker `CMD`

The frontend already supports:

- `VITE_API_URL`
- `VITE_AI_ASSISTANT_URL`
- Vite build output in `dist`
- no frontend secrets

## Backend Deployment: Cloud Run

### 1. Set Variables

Replace these values with your GCP project details:

```bash
PROJECT_ID="your-gcp-project-id"
REGION="asia-southeast1"
SERVICE_NAME="atai-travel-api"
AR_REPO="atai-travel"
IMAGE_NAME="backend"
```

Use any region close to your users. `asia-southeast1` is a practical default for Central/Asia demo latency.

### 2. Enable APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create "$AR_REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Atai Travel containers"
```

Configure Docker auth:

```bash
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

### 4. Build And Push Backend Image

From the project root:

```bash
cd backend
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$IMAGE_NAME:latest" .
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$IMAGE_NAME:latest"
cd ..
```

If Docker is not installed locally, use Cloud Build:

```bash
gcloud builds submit backend \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$IMAGE_NAME:latest"
```

## Database: Cloud SQL PostgreSQL

### 1. Create PostgreSQL Instance

```bash
gcloud sql instances create atai-travel-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region="$REGION"
```

For hackathon/demo this small tier is enough. For real production, choose a larger tier with backups and monitoring.

### 2. Create Database

```bash
gcloud sql databases create atai_travel \
  --instance=atai-travel-db
```

### 3. Create User

```bash
gcloud sql users create atai_user \
  --instance=atai-travel-db \
  --password="CHANGE_THIS_PASSWORD"
```

### 4. Get Instance Connection Name

```bash
gcloud sql instances describe atai-travel-db \
  --format="value(connectionName)"
```

It looks like:

```text
PROJECT_ID:REGION:atai-travel-db
```

### 5. DATABASE_URL For Cloud Run + Cloud SQL Socket

Use the Cloud SQL Unix socket path:

```env
DATABASE_URL=postgresql+psycopg2://atai_user:CHANGE_THIS_PASSWORD@/atai_travel?host=/cloudsql/PROJECT_ID:REGION:atai-travel-db
```

If your password contains special characters, URL-encode it.

## Secrets: Secret Manager

Generate a JWT secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Create secrets:

```bash
echo -n "YOUR_64_CHAR_SECRET" | gcloud secrets create atai-secret-key --data-file=-
echo -n "postgresql+psycopg2://atai_user:CHANGE_THIS_PASSWORD@/atai_travel?host=/cloudsql/PROJECT_ID:REGION:atai-travel-db" | gcloud secrets create atai-database-url --data-file=-
```

Grant the Cloud Run runtime service account permission to read secrets if needed:

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Replace `PROJECT_NUMBER` with:

```bash
gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)"
```

## Deploy Backend To Cloud Run

Use your frontend URL after deploying Firebase. If frontend is not deployed yet, use a temporary placeholder and update it later.

```bash
gcloud run deploy "$SERVICE_NAME" \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$IMAGE_NAME:latest" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --add-cloudsql-instances "PROJECT_ID:REGION:atai-travel-db" \
  --set-env-vars "ENVIRONMENT=production,FRONTEND_URL=https://YOUR_FRONTEND_URL,COOKIE_SECURE=true,COOKIE_SAMESITE=none,ACCESS_TOKEN_EXPIRE_MINUTES=1440" \
  --set-secrets "SECRET_KEY=atai-secret-key:latest,DATABASE_URL=atai-database-url:latest"
```

Check backend:

```bash
gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --format="value(status.url)"
```

Open the URL. It should return:

```json
{"message":"Atai Travel API is running"}
```

## Alembic Migrations

The Docker `CMD` runs:

```bash
python -m alembic upgrade head
```

before starting Uvicorn. This is acceptable for a hackathon demo.

For production later, move migrations into a separate Cloud Run Job or CI/CD step so app startup is not responsible for schema changes.

## Frontend Deployment Option A: Firebase Hosting

This is the recommended hackathon option.

### 1. Install Firebase CLI

```bash
npm install -g firebase-tools
firebase login
```

### 2. Configure Project

Copy:

```text
frontend/.firebaserc.example
```

to:

```text
frontend/.firebaserc
```

Set your GCP/Firebase project ID:

```json
{
  "projects": {
    "default": "YOUR_GCP_PROJECT_ID"
  }
}
```

### 3. Build Frontend

Create `frontend/.env.production` locally:

```env
VITE_API_URL=https://YOUR_CLOUD_RUN_BACKEND_URL
VITE_AI_ASSISTANT_URL=https://think-with-me-bot.lovable.app
```

Build:

```bash
cd frontend
npm install
npm run build
```

### 4. Deploy

```bash
firebase deploy --only hosting --project YOUR_GCP_PROJECT_ID
```

`frontend/firebase.json` already includes SPA fallback:

```json
{
  "source": "**",
  "destination": "/index.html"
}
```

This prevents React Router pages like `/packages/1` or `/ai-assistant` from returning 404 on refresh.

## Frontend Deployment Option B: Cloud Storage + Cloud CDN

Use this only if you already know Cloud Load Balancer/CDN. Firebase Hosting is faster for hackathon.

### Basic Static Bucket

```bash
BUCKET_NAME="atai-travel-frontend"
gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://$BUCKET_NAME"
gsutil web set -m index.html -e index.html "gs://$BUCKET_NAME"
gsutil -m rsync -r -d frontend/dist "gs://$BUCKET_NAME"
```

For proper HTTPS + custom domain + Cloud CDN, create:

- backend bucket
- HTTPS load balancer
- managed SSL certificate
- URL map
- CDN enabled on backend bucket

For React Router, ensure unknown routes fall back to `index.html`. Firebase Hosting handles this more simply.

## Cookie Auth And CORS

### Recommended Hackathon Values

If frontend and backend are on different domains:

Backend:

```env
COOKIE_SECURE=true
COOKIE_SAMESITE=none
FRONTEND_URL=https://YOUR_FIREBASE_HOSTING_URL
```

Frontend:

```env
VITE_API_URL=https://YOUR_CLOUD_RUN_BACKEND_URL
```

Why:

- `COOKIE_SECURE=true` is required because `SameSite=None` cookies must be sent over HTTPS.
- `COOKIE_SAMESITE=none` allows the browser to send the HTTP-only auth cookie from Firebase Hosting to the Cloud Run API domain.
- `FRONTEND_URL` allows CORS credentials from the real frontend domain.
- Axios already uses `withCredentials: true`, so the browser will attach the cookie.

If frontend and backend later share the same site, for example:

```text
https://atai-travel.kg
https://api.atai-travel.kg
```

you can evaluate `COOKIE_SAMESITE=lax`, but for a quick Firebase + Cloud Run cross-domain demo use `none`.

### Common Cookie/CORS Failures

- Login returns 200 but refresh logs out: cookie was not stored or not sent.
- Browser console shows CORS error: `FRONTEND_URL` is missing or wrong.
- Cookie blocked: `COOKIE_SAMESITE=none` without `COOKIE_SECURE=true`.
- Requests hit old backend: frontend was built before `VITE_API_URL` was set.

## Environment Variables

### Backend

| Variable | Example | Notes |
|---|---|---|
| `SECRET_KEY` | Secret Manager `atai-secret-key` | Never commit this |
| `DATABASE_URL` | Secret Manager `atai-database-url` | Cloud SQL PostgreSQL URL |
| `ENVIRONMENT` | `production` | Hides docs and disables dev create_all |
| `FRONTEND_URL` | `https://YOUR_FIREBASE_URL` | Required for CORS |
| `COOKIE_SECURE` | `true` | Required on HTTPS |
| `COOKIE_SAMESITE` | `none` | Required for cross-domain cookie demo |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24 hours |

### Frontend

| Variable | Example | Notes |
|---|---|---|
| `VITE_API_URL` | `https://YOUR_CLOUD_RUN_URL` | Backend API base URL |
| `VITE_AI_ASSISTANT_URL` | `https://think-with-me-bot.lovable.app` | External AI assistant |

## Simple CI/CD

Templates are included:

```text
.github/workflows/gcp-backend-cloud-run.yml
.github/workflows/gcp-frontend-firebase.yml
```

They are meant as starting templates. Before using them, configure GitHub:

Secrets:

```text
GCP_PROJECT_ID
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
CLOUD_SQL_INSTANCE_CONNECTION_NAME
```

Repository variables:

```text
GCP_REGION=asia-southeast1
FRONTEND_URL=https://YOUR_FIREBASE_URL
VITE_API_URL=https://YOUR_CLOUD_RUN_URL
```

The backend workflow:

- installs backend requirements
- runs pytest
- builds Docker image
- pushes to Artifact Registry
- deploys Cloud Run

The frontend workflow:

- installs frontend dependencies
- runs `npm run build`
- deploys `dist` to Firebase Hosting

For hackathon speed, manual deploy is usually faster than setting up Workload Identity. Use CI/CD after the demo if setup takes too long.

## Post-Deployment Checklist

Backend:

- Open Cloud Run URL.
- `/` returns `{"message":"Atai Travel API is running"}`.
- Cloud Run logs show no migration errors.
- Cloud SQL has Atai Travel tables.

Frontend:

- Firebase URL opens homepage.
- Refresh works on `/ai-assistant`.
- Refresh works on protected route after login.

Auth:

- Register works.
- Login sets HTTP-only cookie.
- Refresh keeps session.
- Logout clears cookie.

Product flows:

- `/packages` loads.
- `/ai-assistant` opens external assistant.
- Tourist can create `/travel-request`.
- Partner can open `/partner/requests`.
- Partner can send offer.
- Individual matching page opens for a tourist.

## Troubleshooting

### CORS Error

Check:

```env
FRONTEND_URL=https://YOUR_FRONTEND_URL
```

Then redeploy backend.

### Cookie Not Set

For Firebase + Cloud Run:

```env
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

Also confirm the frontend uses:

```env
VITE_API_URL=https://YOUR_CLOUD_RUN_URL
```

Rebuild and redeploy frontend after changing `VITE_API_URL`.

### 502/503 Cloud Run

Check logs:

```bash
gcloud run services logs read atai-travel-api --region "$REGION"
```

Common causes:

- `SECRET_KEY` missing
- `DATABASE_URL` invalid
- Cloud SQL instance not attached
- migrations failed
- container not listening on `$PORT`

### Migration Failed

Run:

```bash
gcloud run services logs read atai-travel-api --region "$REGION"
```

Check whether:

- Cloud SQL connection name is correct
- `DATABASE_URL` uses the same connection name
- PostgreSQL user/password/database exist
- secret value has no extra newline or typo

### Database Connection Refused

Use Cloud SQL socket URL:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@/DB?host=/cloudsql/PROJECT:REGION:INSTANCE
```

Also deploy with:

```bash
--add-cloudsql-instances PROJECT:REGION:INSTANCE
```

### Frontend Route 404 After Refresh

Use Firebase Hosting with the included `frontend/firebase.json` rewrite:

```json
"rewrites": [{ "source": "**", "destination": "/index.html" }]
```

### VITE_API_URL Not Applied

Vite env variables are build-time variables. Set `VITE_API_URL`, then rebuild:

```bash
npm run build
firebase deploy --only hosting
```

### SECRET_KEY Missing

Backend fails fast if `SECRET_KEY` is missing. Store it in Secret Manager and deploy Cloud Run with:

```bash
--set-secrets "SECRET_KEY=atai-secret-key:latest"
```

## What To Do First For Hackathon

1. Create Cloud SQL PostgreSQL.
2. Create Secret Manager values.
3. Build and deploy backend to Cloud Run.
4. Open backend `/` and confirm it works.
5. Build and deploy frontend to Firebase Hosting.
6. Update backend `FRONTEND_URL` to the Firebase URL.
7. Redeploy backend.
8. Test register/login first.
9. Test travel request and partner offer.
10. Share the Firebase frontend URL.

## What Can Wait Until After Hackathon

- Redis-backed rate limiting.
- Separate migration Cloud Run Job.
- Custom domain setup.
- Cloud CDN optimization.
- Full CI/CD Workload Identity setup.
- Frontend unit tests.
- Playwright E2E tests.
- Production monitoring dashboards.
- Backup and restore drills.
