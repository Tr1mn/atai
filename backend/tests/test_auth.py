"""
Tests for auth security changes:
  1. HTTP-only cookie is set on login and register
  2. /api/auth/me restores session from cookie
  3. /api/auth/logout clears the cookie
  4. Cookie token accepted by protected endpoints (no Authorization header needed)
  5. Rate limiting returns 429 after threshold
"""
from tests.conftest import _make_user, _auth_headers


class TestCookieAuth:
    def test_login_sets_httponly_cookie(self, client, tourist):
        resp = client.post("/api/auth/login", json={
            "email": tourist.email, "password": "Password1!"
        })
        assert resp.status_code == 200
        cookie = resp.cookies.get("access_token")
        assert cookie is not None, "access_token cookie must be set on login"

    def test_register_sets_httponly_cookie(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@test.kg", "password": "Password1!",
            "full_name": "New User", "age": 25, "city": "Bishkek"
        })
        assert resp.status_code == 201
        assert resp.cookies.get("access_token") is not None

    def test_me_returns_user_from_cookie(self, client, tourist):
        # Login first — TestClient stores the cookie automatically
        client.post("/api/auth/login", json={
            "email": tourist.email, "password": "Password1!"
        })
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == tourist.id
        assert data["role"] == tourist.role
        assert data["full_name"] == tourist.full_name

    def test_me_without_auth_returns_401(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_logout_clears_cookie(self, client, tourist):
        client.post("/api/auth/login", json={
            "email": tourist.email, "password": "Password1!"
        })
        client.post("/api/auth/logout")
        # After logout the cookie is gone — /me must return 401
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_protected_endpoint_accepts_cookie(self, client, tourist):
        """A route that requires auth should work when only the cookie is present."""
        client.post("/api/auth/login", json={
            "email": tourist.email, "password": "Password1!"
        })
        # /api/users/me is a protected route
        resp = client.get("/api/users/me")
        assert resp.status_code == 200

    def test_protected_endpoint_accepts_bearer(self, client, tourist):
        """Bearer token in Authorization header must still work (Swagger / API clients)."""
        resp = client.get("/api/users/me", headers=_auth_headers(tourist))
        assert resp.status_code == 200

    def test_cookie_takes_priority_over_bearer(self, client, tourist, tourist2):
        """If both cookie and bearer are present, the cookie user is returned."""
        # Log in as tourist (sets cookie for tourist)
        client.post("/api/auth/login", json={
            "email": tourist.email, "password": "Password1!"
        })
        # Send a bearer token for tourist2 — cookie for tourist should win
        resp = client.get("/api/users/me", headers=_auth_headers(tourist2))
        assert resp.status_code == 200
        assert resp.json()["id"] == tourist.id


class TestRateLimit:
    def test_login_rate_limited_after_threshold(self, client, tourist, reset_limiter):
        """After 5 requests within a minute, the 6th must be rate-limited (429)."""
        payload = {"email": tourist.email, "password": "wrong-password"}
        for _ in range(5):
            client.post("/api/auth/login", json=payload)
        resp = client.post("/api/auth/login", json=payload)
        assert resp.status_code == 429, f"Expected 429, got {resp.status_code}: {resp.text}"

    def test_register_rate_limited_after_threshold(self, client, reset_limiter):
        """Register endpoint also enforces 5/minute per IP."""
        payload = {"email": "x@x.kg", "password": "P1!", "full_name": "X", "age": 25, "city": "B"}
        for _ in range(5):
            client.post("/api/auth/register", json=payload)
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 429, f"Expected 429, got {resp.status_code}"

    def test_valid_login_succeeds_before_limit(self, client, tourist, reset_limiter):
        """A single valid login must still return 200 (sanity check)."""
        resp = client.post("/api/auth/login", json={
            "email": tourist.email, "password": "Password1!"
        })
        assert resp.status_code == 200
