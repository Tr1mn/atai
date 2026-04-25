import os
# Must be set before any app import so pydantic-settings doesn't fail on missing SECRET_KEY.
os.environ.setdefault("SECRET_KEY", "test-only-secret-not-for-production-00000000000000")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_atai.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.partner import Partner
from app.models.package import Package, PackageDate
from app.models.booking import Booking

TEST_DB_URL = "sqlite:///./test_atai.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def reset_limiter():
    """Reset slowapi in-memory rate limit counters before the test runs.
    Apply to rate-limit tests explicitly — not autouse, to avoid overhead."""
    from app.core.rate_limit import limiter
    try:
        # slowapi wraps the `limits` library; MemoryStorage exposes reset().
        limiter._limiter.storage.reset()
    except Exception:
        pass  # if internal API changed, tests still run
    yield
    try:
        limiter._limiter.storage.reset()
    except Exception:
        pass


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


# ── Seed helpers ──────────────────────────────────────────────────────────────

def _make_user(db, email, role="tourist", status="active"):
    u = User(
        email=email,
        password_hash=hash_password("Password1!"),
        full_name="Test User",
        age=25,
        role=role,
        status=status,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_partner(db, user):
    p = Partner(
        user_id=user.id,
        company_name="Test Co",
        commission_rate=15.0,
        status="active",
    )
    db.add(p)
    user.role = "partner"
    db.commit()
    db.refresh(p)
    return p


def _make_package(db, partner_id, price=100.0):
    pkg = Package(
        partner_id=partner_id,
        title="Test Tour",
        destination="Issyk-Kul",
        price=price,
        duration_days=3,
        status="published",
        family_rates_enabled=True,
    )
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    return pkg


def _make_date(db, package_id, slots=1):
    d = PackageDate(
        package_id=package_id,
        start_date=datetime.utcnow() + timedelta(days=30),
        total_slots=slots,
        available_slots=slots,
        status="available",
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def _auth_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


# ── Reusable fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def tourist(db):
    return _make_user(db, "tourist@test.kg")


@pytest.fixture
def tourist2(db):
    return _make_user(db, "tourist2@test.kg")


@pytest.fixture
def partner_user(db):
    return _make_user(db, "partner@test.kg", role="partner")


@pytest.fixture
def partner_user2(db):
    return _make_user(db, "partner2@test.kg", role="partner")


@pytest.fixture
def partner(db, partner_user):
    return _make_partner(db, partner_user)


@pytest.fixture
def partner2(db, partner_user2):
    return _make_partner(db, partner_user2)


@pytest.fixture
def admin_user(db):
    return _make_user(db, "admin@test.kg", role="admin")


@pytest.fixture
def package(db, partner):
    return _make_package(db, partner.id)


@pytest.fixture
def package2(db, partner2):
    return _make_package(db, partner2.id, price=200.0)


@pytest.fixture
def pkg_date(db, package):
    return _make_date(db, package.id, slots=1)


@pytest.fixture
def pkg_date_multi(db, package):
    return _make_date(db, package.id, slots=5)
