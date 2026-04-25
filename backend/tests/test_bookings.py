"""
Tests for production-blocking booking bugs:
  1. Race condition — slots cannot go negative under concurrent requests
  2. Ownership check — partner can only confirm their own packages' bookings
"""
import threading
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from tests.conftest import (
    _auth_headers,
    _make_user,
    _make_partner,
    _make_package,
    _make_date,
    TestingSession,
)
from app.models.package import PackageDate
from app.models.booking import Booking


# ── Helpers ───────────────────────────────────────────────────────────────────

def _book(client, tourist, pkg, date):
    return client.post(
        "/api/bookings/",
        json={
            "package_id": pkg.id,
            "package_date_id": date.id,
            "num_travelers": 1,
            "is_family_booking": False,
        },
        headers=_auth_headers(tourist),
    )


# ── Race condition ────────────────────────────────────────────────────────────

class TestBookingRaceCondition:
    def test_last_slot_sequential_second_fails(self, client, tourist, tourist2, package, pkg_date):
        """Sequential: first booking takes the last slot, second gets 400."""
        r1 = _book(client, tourist, package, pkg_date)
        assert r1.status_code == 201, r1.json()

        r2 = _book(client, tourist2, package, pkg_date)
        assert r2.status_code == 400
        assert "slots" in r2.json()["detail"].lower()

    def test_slots_never_go_negative(self, client, tourist, tourist2, package, pkg_date, db):
        """After two booking attempts on 1 slot, available_slots must be >= 0."""
        _book(client, tourist, package, pkg_date)
        _book(client, tourist2, package, pkg_date)

        db.refresh(pkg_date)
        assert pkg_date.available_slots >= 0, (
            f"available_slots went negative: {pkg_date.available_slots}"
        )

    def test_concurrent_only_one_booking_created(self, tourist, tourist2, package, pkg_date, db):
        """Two threads racing for the last slot: exactly one booking must be created."""
        # Capture primitive values before threads start — SQLAlchemy ORM objects
        # are session-bound and cannot be safely shared across thread boundaries.
        pkg_id = package.id
        date_id = pkg_date.id
        tok1 = create_access_token({"sub": str(tourist.id)})
        tok2 = create_access_token({"sub": str(tourist2.id)})

        results = []
        lock = threading.Lock()

        def attempt(token):
            c = TestClient(app)
            resp = c.post(
                "/api/bookings/",
                json={"package_id": pkg_id, "package_date_id": date_id,
                      "num_travelers": 1, "is_family_booking": False},
                headers={"Authorization": f"Bearer {token}"},
            )
            with lock:
                results.append(resp.status_code)

        t1 = threading.Thread(target=attempt, args=(tok1,))
        t2 = threading.Thread(target=attempt, args=(tok2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert results.count(201) == 1, f"Expected exactly 1 success, got: {results}"
        assert results.count(400) == 1, f"Expected exactly 1 failure, got: {results}"

        db.refresh(pkg_date)
        assert pkg_date.available_slots == 0
        assert pkg_date.available_slots >= 0

    def test_full_slot_shows_full_status(self, client, tourist, package, pkg_date, db):
        """After booking the last slot the date status becomes 'full'."""
        _book(client, tourist, package, pkg_date)
        db.refresh(pkg_date)
        assert pkg_date.status == "full"

    def test_multiple_slots_all_bookable(self, client, tourist, tourist2, package, pkg_date_multi, db):
        """With 5 slots, two sequential bookings should both succeed."""
        r1 = _book(client, tourist, package, pkg_date_multi)
        r2 = _book(client, tourist2, package, pkg_date_multi)
        assert r1.status_code == 201
        assert r2.status_code == 201
        db.refresh(pkg_date_multi)
        assert pkg_date_multi.available_slots == 3


# ── Ownership check ───────────────────────────────────────────────────────────

class TestConfirmOwnership:
    def _create_paid_booking(self, client, tourist, package, date):
        r = _book(client, tourist, package, date)
        assert r.status_code == 201
        booking_id = r.json()["id"]
        pay = client.post(f"/api/bookings/{booking_id}/pay", headers=_auth_headers(tourist))
        assert pay.status_code == 200
        return booking_id

    def test_partner_confirms_own_booking(self, client, tourist, partner_user, partner, package, pkg_date):
        """Partner can confirm a booking on their own package."""
        booking_id = self._create_paid_booking(client, tourist, package, pkg_date)
        resp = client.post(
            f"/api/bookings/{booking_id}/confirm",
            headers=_auth_headers(partner_user),
        )
        assert resp.status_code == 200, resp.json()
        assert resp.json()["status"] == "confirmed"

    def test_partner_cannot_confirm_other_partners_booking(
        self, client, tourist, partner_user2, partner2, package, package2, pkg_date, db
    ):
        """Partner B cannot confirm a booking that belongs to Partner A's package."""
        date2 = _make_date(db, package2.id, slots=1)
        booking_id = self._create_paid_booking(client, tourist, package, pkg_date)

        # partner_user2 owns package2, NOT package — must be rejected
        resp = client.post(
            f"/api/bookings/{booking_id}/confirm",
            headers=_auth_headers(partner_user2),
        )
        assert resp.status_code == 403, resp.json()
        assert "own" in resp.json()["detail"].lower()

    def test_admin_can_confirm_any_booking(self, client, tourist, admin_user, package, pkg_date):
        """Admin is not restricted by package ownership."""
        booking_id = self._create_paid_booking(client, tourist, package, pkg_date)
        resp = client.post(
            f"/api/bookings/{booking_id}/confirm",
            headers=_auth_headers(admin_user),
        )
        assert resp.status_code == 200, resp.json()

    def test_tourist_cannot_confirm(self, client, tourist, tourist2, package, pkg_date):
        """Regular tourists must be rejected regardless of booking ownership."""
        booking_id = self._create_paid_booking(client, tourist, package, pkg_date)
        resp = client.post(
            f"/api/bookings/{booking_id}/confirm",
            headers=_auth_headers(tourist2),
        )
        assert resp.status_code == 403

    def test_confirm_unpaid_booking_fails(self, client, tourist, partner_user, partner, package, pkg_date):
        """Confirming a booking that hasn't been paid yet must return 400."""
        r = _book(client, tourist, package, pkg_date)
        booking_id = r.json()["id"]
        resp = client.post(
            f"/api/bookings/{booking_id}/confirm",
            headers=_auth_headers(partner_user),
        )
        assert resp.status_code == 400
