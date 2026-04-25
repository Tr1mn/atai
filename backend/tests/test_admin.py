"""
Tests for production-blocking admin bugs:
  1. Commission uses per-partner commission_rate, not hardcoded 12%
  2. Dashboard uses SQL aggregation — no full table scan into Python memory
"""
from unittest.mock import patch

from tests.conftest import (
    _auth_headers,
    _make_user,
    _make_partner,
    _make_package,
    _make_date,
    TestingSession,
)
from app.models.booking import Booking
from app.models.package import PackageDate
from datetime import datetime, timedelta


# ── Helpers ───────────────────────────────────────────────────────────────────

def _seed_confirmed_booking(db, tourist, partner, price, commission_rate=None):
    """Create a confirmed booking and return (booking, partner) for assertion."""
    if commission_rate is not None:
        partner.commission_rate = commission_rate
        db.commit()

    pkg = _make_package(db, partner.id, price=price)
    date = _make_date(db, pkg.id, slots=5)

    booking = Booking(
        user_id=tourist.id,
        package_id=pkg.id,
        package_date_id=date.id,
        status="confirmed",
        num_travelers=1,
        base_price=price,
        total_price=price,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        paid_at=datetime.utcnow(),
        confirmed_at=datetime.utcnow(),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


# ── Commission calculation ────────────────────────────────────────────────────

class TestAdminCommission:
    def test_commission_uses_partner_rate_not_hardcoded_12(
        self, client, admin_user, tourist, partner_user, partner, db
    ):
        """GMV=$1000, partner commission_rate=20% → platform_commission=200, not 120."""
        partner.commission_rate = 20.0
        db.commit()

        _seed_confirmed_booking(db, tourist, partner, price=1000.0, commission_rate=20.0)

        resp = client.get("/api/admin/dashboard", headers=_auth_headers(admin_user))
        assert resp.status_code == 200, resp.json()
        data = resp.json()

        assert data["gmv"] == 1000.0
        assert data["platform_commission"] == 200.0, (
            f"Expected 200.0 (20% of 1000), got {data['platform_commission']}. "
            "Commission still uses hardcoded 12% instead of partner.commission_rate."
        )

    def test_commission_blended_across_partners(
        self, client, admin_user, tourist, partner_user, partner,
        partner_user2, partner2, db
    ):
        """
        Partner A: $500 booking, 10% rate → $50 commission
        Partner B: $200 booking, 25% rate → $50 commission
        Total commission = $100
        """
        _seed_confirmed_booking(db, tourist, partner, price=500.0, commission_rate=10.0)
        _seed_confirmed_booking(db, tourist, partner2, price=200.0, commission_rate=25.0)

        resp = client.get("/api/admin/dashboard", headers=_auth_headers(admin_user))
        data = resp.json()

        assert data["gmv"] == 700.0
        assert data["platform_commission"] == 100.0, (
            f"Expected blended commission=100.0, got {data['platform_commission']}"
        )

    def test_pending_bookings_excluded_from_gmv(
        self, client, admin_user, tourist, partner_user, partner, db
    ):
        """Pending-payment bookings must not be counted in GMV or commission."""
        pkg = _make_package(db, partner.id, price=500.0)
        date = _make_date(db, pkg.id, slots=5)
        pending = Booking(
            user_id=tourist.id,
            package_id=pkg.id,
            package_date_id=date.id,
            status="pending_payment",
            num_travelers=1,
            base_price=500.0,
            total_price=500.0,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(pending)
        db.commit()

        resp = client.get("/api/admin/dashboard", headers=_auth_headers(admin_user))
        data = resp.json()

        assert data["gmv"] == 0.0
        assert data["platform_commission"] == 0.0


# ── Dashboard does not load all bookings into Python memory ──────────────────

class TestAdminDashboardEfficiency:
    def test_dashboard_does_not_call_booking_all(
        self, client, admin_user, tourist, partner_user, partner, db
    ):
        """
        Regression guard: the old code did db.query(Booking).all() which loads
        every row into Python. We patch Query.__iter__ to detect if the result
        set is fully iterated (which .all() triggers) on the Booking table.
        """
        _seed_confirmed_booking(db, tourist, partner, price=100.0)

        booking_all_called = []

        original_all = TestingSession.__class__.__mro__  # just a reference check

        # Patch sqlalchemy Query.all to track if it's called for Booking queries
        from sqlalchemy.orm import Query
        original_all_method = Query.all

        def tracking_all(self):
            entities = [d["entity"] for d in self.column_descriptions if "entity" in d]
            if any(e is Booking for e in entities):
                booking_all_called.append(True)
            return original_all_method(self)

        with patch.object(Query, "all", tracking_all):
            resp = client.get("/api/admin/dashboard", headers=_auth_headers(admin_user))

        assert resp.status_code == 200
        assert not booking_all_called, (
            "db.query(Booking).all() was called — this loads all rows into memory. "
            "Use SQL aggregation (func.count/func.sum) instead."
        )

    def test_dashboard_non_admin_rejected(self, client, tourist):
        resp = client.get("/api/admin/dashboard", headers=_auth_headers(tourist))
        assert resp.status_code == 403

    def test_dashboard_counts_are_correct(
        self, client, admin_user, tourist, partner_user, partner, db
    ):
        """Verify dashboard counters match actual DB state."""
        _seed_confirmed_booking(db, tourist, partner, price=300.0)

        resp = client.get("/api/admin/dashboard", headers=_auth_headers(admin_user))
        data = resp.json()

        assert data["total_bookings"] == 1
        assert data["confirmed_bookings"] == 1
        assert data["gmv"] == 300.0
        assert data["total_users"] >= 2   # tourist + partner_user
        assert data["total_partners"] >= 1
