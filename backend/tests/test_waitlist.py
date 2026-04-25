"""
Tests for waitlist position assignment:
  - position uses MAX+1, not count+1
  - no duplicate positions when entries are removed
  - duplicate join is rejected
"""
from app.models.booking import WaitingList
from tests.conftest import _make_user, _auth_headers, _make_date


class TestWaitlistPosition:
    def test_first_entry_gets_position_1(self, client, tourist, package, pkg_date):
        resp = client.post(f"/api/bookings/{pkg_date.id}/waitlist",
                           headers=_auth_headers(tourist))
        assert resp.status_code == 201
        assert resp.json()["position"] == 1

    def test_second_entry_gets_position_2(self, client, tourist, tourist2, package, pkg_date):
        client.post(f"/api/bookings/{pkg_date.id}/waitlist", headers=_auth_headers(tourist))
        resp = client.post(f"/api/bookings/{pkg_date.id}/waitlist", headers=_auth_headers(tourist2))
        assert resp.status_code == 201
        assert resp.json()["position"] == 2

    def test_position_after_entry_removal_no_duplicate(self, client, tourist, tourist2, package, pkg_date, db):
        """
        Scenario: user1 joins (pos=1), user2 joins (pos=2), user1's entry is
        manually removed. A new user should get pos=3, not pos=2 (which would
        duplicate user2's position). MAX+1 guarantees uniqueness; count+1 would not.
        """
        client.post(f"/api/bookings/{pkg_date.id}/waitlist", headers=_auth_headers(tourist))
        client.post(f"/api/bookings/{pkg_date.id}/waitlist", headers=_auth_headers(tourist2))

        # Simulate cancellation by removing user1's entry directly
        entry = db.query(WaitingList).filter(
            WaitingList.user_id == tourist.id,
            WaitingList.package_date_id == pkg_date.id,
        ).first()
        db.delete(entry)
        db.commit()

        # Now count=1, MAX=2. A new user should get MAX+1=3, not count+1=2.
        user3 = _make_user(db, "user3@test.kg")
        resp = client.post(f"/api/bookings/{pkg_date.id}/waitlist",
                           headers=_auth_headers(user3))
        assert resp.status_code == 201
        assert resp.json()["position"] == 3, (
            f"Expected position 3 (MAX+1), got {resp.json()['position']}. "
            "count+1 would have incorrectly returned 2, duplicating user2's position."
        )

    def test_duplicate_join_rejected(self, client, tourist, package, pkg_date):
        client.post(f"/api/bookings/{pkg_date.id}/waitlist", headers=_auth_headers(tourist))
        resp = client.post(f"/api/bookings/{pkg_date.id}/waitlist", headers=_auth_headers(tourist))
        assert resp.status_code == 400
        assert "waiting list" in resp.json()["detail"].lower()

    def test_waitlist_isolated_between_dates(self, client, tourist, tourist2, package, db):
        """Positions are independent per package_date, not global."""
        date1 = _make_date(db, package.id, slots=0)
        date2 = _make_date(db, package.id, slots=0)
        client.post(f"/api/bookings/{date1.id}/waitlist", headers=_auth_headers(tourist))
        client.post(f"/api/bookings/{date1.id}/waitlist", headers=_auth_headers(tourist2))
        # First entry on date2 should be position 1, not 3
        resp = client.post(f"/api/bookings/{date2.id}/waitlist", headers=_auth_headers(tourist))
        assert resp.status_code == 201
        assert resp.json()["position"] == 1
