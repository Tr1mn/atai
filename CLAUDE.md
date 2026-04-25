# CLAUDE.md — Atai Travel

Everything a new session needs to understand this project without re-reading every file.

---

## What this project is

Travel marketplace MVP for Kyrgyzstan. Tourists browse and book tour packages from local partner operators. Features: package catalog, booking with family discounts, social matching (like/match), group trip organization, partner dashboard, admin moderation panel.

**UI language:** Russian. **Code language:** English.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy (sync) + SQLite |
| Frontend | React 18 + React Router v6 + Axios + Tailwind CSS |
| Build | Vite |
| Auth | JWT via `python-jose`, bcrypt passwords |
| Tests | pytest + httpx (backend only) |

---

## How to run

```bash
# Backend — from backend/
pip install -r requirements.txt
python seed.py          # one-time: creates DB + 5 demo users + 3 packages
uvicorn app.main:app --reload --port 8000

# Frontend — from frontend/
npm install
npm run dev             # http://localhost:5173

# API docs (dev only)
http://localhost:8000/docs
```

**Tests:**
```bash
cd backend
python -m pytest tests/ -v
```

---

## Environment setup

The server **will not start** without a `.env` file in `backend/`. `SECRET_KEY` has no default.

```bash
# backend/.env  (already created, gitignored)
SECRET_KEY=<64-char hex>    # generate: python -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=sqlite:///./atai_travel.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Copy `backend/.env.example` as a template.

---

## Project structure

```
atai-travel/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router registration, DB init
│   │   ├── config.py            # pydantic-settings, reads from .env
│   │   ├── database.py          # SQLAlchemy engine + SessionLocal + get_db
│   │   ├── core/
│   │   │   └── security.py      # JWT create/decode, bcrypt, get_current_user, require_admin/partner
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User (tourist|partner|admin roles)
│   │   │   ├── partner.py       # Partner (agency|hotel|transport)
│   │   │   ├── package.py       # Package + PackageDate
│   │   │   ├── booking.py       # Booking + WaitingList
│   │   │   ├── trip.py          # Trip + TripMembers
│   │   │   └── social.py        # Like, Match, Message, Review, Complaint
│   │   ├── routers/             # FastAPI route handlers
│   │   │   ├── auth.py          # POST /api/auth/register|login
│   │   │   ├── users.py         # GET|PUT /api/users/me, browse, like, match
│   │   │   ├── packages.py      # GET /api/packages/, POST (partner)
│   │   │   ├── bookings.py      # POST book/pay/confirm/cancel, waitlist
│   │   │   ├── trips.py         # CRUD trips, join/approve/reject
│   │   │   ├── partners.py      # Apply, my packages/bookings/stats
│   │   │   └── admin.py         # Dashboard, moderate users/partners/packages
│   │   └── schemas/             # Pydantic request/response schemas
│   ├── tests/
│   │   ├── conftest.py          # Test DB, fixtures, seed helpers, _auth_headers
│   │   ├── test_bookings.py     # Race condition + ownership check tests
│   │   └── test_admin.py        # Commission calc + dashboard aggregation tests
│   ├── seed.py                  # Seeds demo data into DB
│   ├── requirements.txt
│   ├── .env                     # GITIGNORED — real secrets
│   └── .env.example             # Template
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Route definitions + AuthProvider wrapper
│   │   ├── api/client.js        # Axios instance, token interceptor, 401 auto-logout
│   │   ├── context/AuthContext.jsx  # Auth state, login/register/logout, localStorage
│   │   ├── components/          # Navbar, Footer, PackageCard, TripCard
│   │   └── pages/               # One file per page/route
│   ├── index.html
│   ├── vite.config.js
│   └── tailwind.config.js
├── .gitignore                   # Covers .env, *.db, __pycache__, node_modules, dist
├── CLAUDE.md                    # This file
└── start.bat                    # Windows convenience script
```

---

## Demo accounts (seeded by seed.py)

| Role | Email | Password |
|---|---|---|
| Admin | admin@atai.kg | admin123 |
| Partner | partner@nomad.kg | partner123 |
| Tourist | aizat@mail.kg | user123 |
| Tourist | temirlan@mail.kg | user123 |
| Tourist | sarah@gmail.com | user123 |

---

## Database schema (key tables)

No migration system — schema is created by `Base.metadata.create_all()` in `main.py` on startup. Any schema change requires dropping and recreating the DB (or adding Alembic, which is a pending improvement).

```
User            id, email, password_hash, role (tourist|partner|admin), status, age, city, ...
Partner         id, user_id→User, company_name, commission_rate (default 12.0%), status
Package         id, partner_id→Partner, title, price, status (draft→under_moderation→published), ...
PackageDate     id, package_id→Package, start_date, total_slots, available_slots, status
Booking         id, user_id, package_id, package_date_id, status, total_price, expires_at (24h)
WaitingList     id, user_id, package_date_id, position, status
Trip            id, organizer_id→User, title, destination, min/max_size, status
TripMembers     id, trip_id, user_id, status (pending|accepted|rejected)
Like            from_user_id, to_user_id
Match           user1_id, user2_id  (created when mutual like exists)
Message         match_id, sender_id, content
Review          user_id, package_id, booking_id (unique), rating, text
Complaint       reporter_id, target_user_id, reason, status
```

---

## Auth flow

- JWT HS256, 24h expiry, no refresh tokens
- Token stored in `localStorage` (known security debt — should be HTTP-only cookie)
- `create_access_token({"sub": str(user.id)})` — **sub must be a string** (JWT RFC 7519)
- `get_current_user` decodes with `int(payload.get("sub"))` to convert back
- Middleware: Axios interceptor attaches `Authorization: Bearer <token>` to every request, auto-logout on 401

**IMPORTANT:** Always use `str(user.id)` when creating tokens and `int(raw_sub)` when decoding. Using an integer sub directly will cause `JWTClaimsError` with `python-jose` ≥ 3.4.

---

## Business logic essentials

### Booking flow
1. Check `available_slots > 0` via atomic `UPDATE WHERE available_slots > 0` (rowcount check)
2. Apply family discount: 20% for 2-3 travelers, 30% for 4+ (only if `package.family_rates_enabled`)
3. Create booking with `status="pending_payment"`, `expires_at = now + 24h`
4. `POST /pay` → `status="paid"`
5. `POST /confirm` → `status="confirmed"` (partner/admin only, partner must own the package)
6. On cancel → restore `available_slots`

### Booking inventory race condition fix
The old code did read-then-decrement (not atomic). The fix uses:
```python
result = db.execute(
    update(PackageDate)
    .where(PackageDate.id == id, PackageDate.available_slots > 0)
    .values(available_slots=PackageDate.available_slots - 1)
    .execution_options(synchronize_session=False)
)
db.flush()
if result.rowcount == 0:
    raise HTTPException(400, "No slots available")
```

### Partner ownership on confirm
Partners can only confirm bookings for their own packages. Check: `Package.partner_id == Partner.id` where `Partner.user_id == current_user.id`.

### Commission calculation
`admin.py` calculates commission via SQL join, using each partner's actual `commission_rate`:
```python
func.sum(Booking.total_price * Partner.commission_rate / 100)
# joined: Booking → Package → Partner
```
Never hardcode 12% — each partner has their own rate.

### Matching system
Like A→B + Like B→A = Match. Mutual like creates a `Match` row. Messages are scoped to `match_id`.

### Waiting list
Manual — no automatic promotion when slots free up. This is a known missing feature.

---

## API routes summary

```
POST /api/auth/register
POST /api/auth/login

GET  /api/users/me            PUT /api/users/me
GET  /api/users/              (browse, excludes self + already-liked)
POST /api/users/{id}/like
GET  /api/users/me/matches
POST /api/users/{id}/report

GET  /api/packages/           POST /api/packages/ (partner)
GET  /api/packages/{id}

POST /api/bookings/           (create)
POST /api/bookings/{id}/pay
POST /api/bookings/{id}/confirm   (partner owns package, or admin)
POST /api/bookings/{id}/cancel
GET  /api/bookings/me
POST /api/bookings/{date_id}/waitlist

GET  /api/trips/              POST /api/trips/
GET  /api/trips/{id}
POST /api/trips/{id}/join
POST /api/trips/{id}/approve/{user_id}
POST /api/trips/{id}/reject/{user_id}

POST /api/partners/apply
GET  /api/partners/me/packages
GET  /api/partners/me/bookings
GET  /api/partners/me/stats

GET  /api/admin/dashboard
GET  /api/admin/users         PUT /api/admin/users/{id}/status
GET  /api/admin/partners      PUT /api/admin/partners/{id}/approve|suspend
GET  /api/admin/packages/pending  PUT /api/admin/packages/{id}/approve|reject
GET  /api/admin/complaints    PUT /api/admin/complaints/{id}/resolve
```

---

## Auth cookie details

Login and register set an HTTP-only cookie `access_token`.
- Dev (`ENVIRONMENT=development`): `SameSite=Lax`, `Secure=False` — works on HTTP localhost
- Prod (`ENVIRONMENT=production`): `SameSite=Strict`, `Secure=True` — requires HTTPS

`get_current_user` checks cookie first, then `Authorization: Bearer` header (fallback for Swagger/API clients).

Frontend uses `withCredentials: true` on all axios requests. No token in localStorage.
On startup, `AuthContext` calls `GET /api/auth/me` to restore user session from cookie.

## Alembic migrations

```bash
# First-time setup (already done):
cd backend
alembic init alembic           # already initialized
alembic revision --autogenerate -m "describe change"
alembic upgrade head

# In production: run alembic upgrade head instead of relying on create_all.
# In development: create_all still runs on startup (ENVIRONMENT=development).
```

Migration files live in `backend/alembic/versions/`. Never delete them.

---

## Frontend routing

```
/                     Home (hero, stats, featured packages)
/login                /register
/packages             Package catalog with filters
/packages/:id         Package detail (itinerary, dates, reviews)
/packages/:id/book    Booking form  ← depends on React Router state, breaks on refresh
/my-bookings
/trips                /trips/:id
/matching
/profile
/become-partner
/partner              Partner dashboard (partner|admin only)
/admin                Admin panel (admin only)
```

**Known frontend bug:** `/packages/:id/book` reads package data from React Router `location.state`. Refreshing the page loses the state and shows an error. Should fetch from API using URL param instead.

---

## Test infrastructure

Tests use an isolated SQLite DB (`test_atai.db`, gitignored). The `clean_db` fixture (autouse) creates tables before each test and drops them after.

```python
# conftest.py pattern
os.environ.setdefault("SECRET_KEY", "test-only-secret")  # must be before any app import
app.dependency_overrides[get_db] = override_get_db        # redirect all DB access to test DB
```

**Important:** Never pass SQLAlchemy ORM objects across thread boundaries in tests. Capture `.id` values and tokens as plain Python values before spawning threads.

---

## What has been audited and fixed (2026-04-25)

| # | Fix | File |
|---|---|---|
| 1 | SECRET_KEY requires .env, no hardcoded default | `config.py` |
| 2 | JWT sub encoded as `str(user.id)`, decoded with `int()` | `auth.py`, `security.py` |
| 3 | Booking race condition → atomic UPDATE WHERE | `routers/bookings.py` |
| 4 | Partner ownership check on confirm | `routers/bookings.py` |
| 5 | Admin commission uses partner.commission_rate | `routers/admin.py` |
| 6 | Admin dashboard SQL aggregation, no `.all()` | `routers/admin.py` |
| 7 | .gitignore for .env, *.db, __pycache__ | `.gitignore` |
| 8 | 16 backend tests covering all above | `tests/` |

---

## Remaining work

**Done (patch 2):**
- [x] HTTP-only cookie auth — no more localStorage
- [x] Rate limiting on /api/auth/login and /register (5/minute)
- [x] /docs hidden in production (ENVIRONMENT=production)
- [x] CORS narrowed: explicit methods and headers
- [x] create_all removed from production startup
- [x] Alembic initialized, initial migration generated
- [x] Waitlist position uses MAX+1 (not count+1)
- [x] Booking.jsx fetches package from API (works on refresh/direct URL)
- [x] Client-side form validation on booking

**Still pending:**
- [ ] Migrate SQLite → PostgreSQL (required before production)
- [ ] Add waiting list auto-promotion on booking cancellation
- [ ] Add dispute endpoint (`POST /api/bookings/{id}/dispute`)
- [ ] Add transactional email notifications
- [ ] Add `lang="ru"` and SEO meta tags to `index.html`
- [ ] Add React Error Boundary in `App.jsx`
- [ ] No password complexity rules — only min 6 chars enforced on frontend
