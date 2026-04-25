"""Tests for the individual matching feature: /individual, /skip, contacts privacy."""
import pytest
from tests.conftest import _make_user, _auth_headers


# ── /individual endpoint ──────────────────────────────────────────────────────

def test_individual_excludes_self(client, db, tourist):
    r = client.get("/api/users/individual", headers=_auth_headers(tourist))
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    assert tourist.id not in ids


def test_individual_excludes_already_liked(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))
    r = client.get("/api/users/individual", headers=_auth_headers(tourist))
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    assert tourist2.id not in ids


def test_individual_excludes_skipped(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist2.id}/skip", headers=_auth_headers(tourist))
    r = client.get("/api/users/individual", headers=_auth_headers(tourist))
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    assert tourist2.id not in ids


def test_individual_excludes_blocked_users(client, db, tourist):
    blocked = _make_user(db, "blocked@test.kg", status="blocked")
    r = client.get("/api/users/individual", headers=_auth_headers(tourist))
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    assert blocked.id not in ids


def test_individual_excludes_partners_and_admins(client, db, tourist):
    partner = _make_user(db, "part@test.kg", role="partner")
    admin = _make_user(db, "adm@test.kg", role="admin")
    r = client.get("/api/users/individual", headers=_auth_headers(tourist))
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    assert partner.id not in ids
    assert admin.id not in ids


def test_individual_requires_auth(client):
    r = client.get("/api/users/individual")
    assert r.status_code == 401


# ── /skip endpoint ────────────────────────────────────────────────────────────

def test_skip_returns_skipped_true(client, db, tourist, tourist2):
    r = client.post(f"/api/users/{tourist2.id}/skip", headers=_auth_headers(tourist))
    assert r.status_code == 201
    assert r.json()["skipped"] is True


def test_skip_self_rejected(client, db, tourist):
    r = client.post(f"/api/users/{tourist.id}/skip", headers=_auth_headers(tourist))
    assert r.status_code == 400


def test_skip_duplicate_is_idempotent(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist2.id}/skip", headers=_auth_headers(tourist))
    r = client.post(f"/api/users/{tourist2.id}/skip", headers=_auth_headers(tourist))
    assert r.status_code == 201  # second skip silently succeeds


# ── contacts privacy ──────────────────────────────────────────────────────────

def test_contacts_not_in_user_public(client, db, tourist, tourist2):
    """GET /api/users/{id} must never expose contacts."""
    tourist2.telegram = "@secret"
    db.commit()
    r = client.get(f"/api/users/{tourist2.id}", headers=_auth_headers(tourist))
    assert r.status_code == 200
    data = r.json()
    assert "telegram" not in data
    assert "phone" not in data
    assert "whatsapp" not in data
    assert "instagram" not in data


def test_contacts_in_me(client, db, tourist):
    """GET /api/users/me must include contacts."""
    tourist.telegram = "@myhandle"
    tourist.phone = "+996700000000"
    db.commit()
    r = client.get("/api/users/me", headers=_auth_headers(tourist))
    assert r.status_code == 200
    data = r.json()
    assert data["telegram"] == "@myhandle"
    assert data["phone"] == "+996700000000"


def test_contacts_visible_in_matches_after_mutual_like(client, db, tourist, tourist2):
    """After mutual like, GET /api/users/me/matches returns contacts of the matched user."""
    tourist2.telegram = "@traveler"
    db.commit()

    client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))
    r = client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    assert r.json()["matched"] is True

    r = client.get("/api/users/me/matches", headers=_auth_headers(tourist))
    assert r.status_code == 200
    matches = r.json()
    assert len(matches) == 1
    assert matches[0]["user"]["telegram"] == "@traveler"


def test_contacts_not_in_matches_without_mutual_like(client, db, tourist, tourist2):
    """No mutual like → no match → matches list is empty."""
    tourist2.telegram = "@hidden"
    db.commit()

    client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))

    r = client.get("/api/users/me/matches", headers=_auth_headers(tourist))
    assert r.status_code == 200
    assert r.json() == []


# ── like returns contact_unlocked ─────────────────────────────────────────────

def test_like_returns_contact_unlocked_false_without_match(client, db, tourist, tourist2):
    r = client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))
    assert r.status_code == 201
    data = r.json()
    assert data["matched"] is False
    assert data["contact_unlocked"] is False


def test_like_returns_contact_unlocked_true_on_match(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    r = client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))
    assert r.status_code == 201
    data = r.json()
    assert data["matched"] is True
    assert data["contact_unlocked"] is True


# ── incoming likes ────────────────────────────────────────────────────────────

def test_incoming_likes_shows_user_who_liked_current_user(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))

    r = client.get("/api/users/me/incoming-likes", headers=_auth_headers(tourist))
    assert r.status_code == 200
    incoming = r.json()
    assert len(incoming) == 1
    assert incoming[0]["user"]["id"] == tourist2.id
    assert "like_id" in incoming[0]
    assert "liked_at" in incoming[0]


def test_incoming_likes_hides_contacts_before_match(client, db, tourist, tourist2):
    tourist2.phone = "+996700123456"
    tourist2.telegram = "@hidden_traveler"
    tourist2.whatsapp = "+996700123456"
    tourist2.instagram = "@hidden_instagram"
    db.commit()

    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    r = client.get("/api/users/me/incoming-likes", headers=_auth_headers(tourist))

    user = r.json()[0]["user"]
    assert "phone" not in user
    assert "telegram" not in user
    assert "whatsapp" not in user
    assert "instagram" not in user
    assert "email" not in user


def test_incoming_likes_excludes_liked_back_users(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))

    r = client.get("/api/users/me/incoming-likes", headers=_auth_headers(tourist))
    assert r.status_code == 200
    assert r.json() == []


def test_incoming_likes_excludes_already_matched_users(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))

    r = client.get("/api/users/me/incoming-likes", headers=_auth_headers(tourist))
    assert r.status_code == 200
    assert r.json() == []


def test_incoming_likes_excludes_skipped_users(client, db, tourist, tourist2):
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    client.post(f"/api/users/{tourist2.id}/skip", headers=_auth_headers(tourist))

    r = client.get("/api/users/me/incoming-likes", headers=_auth_headers(tourist))
    assert r.status_code == 200
    assert r.json() == []


def test_incoming_likes_excludes_partner_and_admin(client, db, tourist):
    partner = _make_user(db, "incoming-partner@test.kg", role="partner")
    admin = _make_user(db, "incoming-admin@test.kg", role="admin")
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(partner))
    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(admin))

    r = client.get("/api/users/me/incoming-likes", headers=_auth_headers(tourist))
    assert r.status_code == 200
    assert r.json() == []


def test_mutual_like_from_incoming_unlocks_contacts_in_matches(client, db, tourist, tourist2):
    tourist2.telegram = "@traveler_after_match"
    tourist2.phone = "+996700222333"
    db.commit()

    client.post(f"/api/users/{tourist.id}/like", headers=_auth_headers(tourist2))
    r = client.post(f"/api/users/{tourist2.id}/like", headers=_auth_headers(tourist))
    assert r.status_code == 201
    assert r.json()["matched"] is True

    matches = client.get("/api/users/me/matches", headers=_auth_headers(tourist)).json()
    assert matches[0]["user"]["telegram"] == "@traveler_after_match"
    assert matches[0]["user"]["phone"] == "+996700222333"


# ── update contacts via PUT /me ───────────────────────────────────────────────

def test_update_contacts_via_profile(client, db, tourist):
    r = client.put("/api/users/me", json={"telegram": "@new_handle", "phone": "+996700111222"}, headers=_auth_headers(tourist))
    assert r.status_code == 200
    data = r.json()
    assert data["telegram"] == "@new_handle"
    assert data["phone"] == "+996700111222"
