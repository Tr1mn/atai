from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./atai_travel.db"
    SECRET_KEY: str  # required — no default, fails fast if .env is missing
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_URL: str = ""
    COOKIE_SAMESITE: str = "lax"
    COOKIE_SECURE: bool = False
    # "development" → create_all on startup, /docs visible, insecure cookies
    # "production"  → migrations via alembic, /docs hidden, secure cookies
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
