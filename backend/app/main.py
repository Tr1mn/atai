from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .config import settings
from .database import engine, Base
from .core.rate_limit import limiter
from .routers import auth, users, packages, bookings, trips, partners, admin, travel_requests

_is_prod = settings.ENVIRONMENT == "production"
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    settings.FRONTEND_URL,
]
allowed_origins = [origin for origin in allowed_origins if origin]

app = FastAPI(
    title="Atai Travel API",
    version="1.0.0",
    # Hide interactive docs in production — they expose the full API surface.
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Database ──────────────────────────────────────────────────────────────────
# In production, run: alembic upgrade head
# In development, create_all is a convenience so seed.py works without Alembic.
if not _is_prod:
    Base.metadata.create_all(bind=engine)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(packages.router)
app.include_router(bookings.router)
app.include_router(trips.router)
app.include_router(partners.router)
app.include_router(admin.router)
app.include_router(travel_requests.router)

@app.get("/")
def root():
    return {"message": "Atai Travel API is running"}
