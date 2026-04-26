# About Atai Travel — Comprehensive Project Analysis

Atai Travel is a travel-marketplace MVP for Kyrgyzstan. The product connects tourists, local tour operators, and individual travelers in one web application. Users can browse and book tours, create custom travel requests, find companions with similar interests, and use an external AI assistant to get trip ideas.

The project is a functional prototype with a React frontend and a FastAPI backend. It includes authentication, role-based flows, package discovery, bookings, partner management, admin moderation, travel request offers, individual matching, and an AI assistant entry point.

---

## Product Goal

Atai Travel helps travelers discover Kyrgyzstan through three main paths:

- Ready-made tours from verified partners.
- Custom trip requests where agencies send offers.
- Social travel matching for finding people with similar interests.

The platform is focused on routes and destinations in Kyrgyzstan such as Issyk-Kul, Karakol, Ala-Kul, Altyn-Arashan, Jeti-Oguz, Skazka Canyon, Son-Kul, Ala-Archa, Chon-Kemin, Osh, Sulaiman-Too, Tash-Rabat, Sary-Chelek, Arslanbob, Kel-Suu, the Alay Valley, and Peak Lenin.

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Backend | FastAPI | 0.103.2 |
| ORM | SQLAlchemy (sync) | 2.0.21 |
| Database | SQLite (dev) / PostgreSQL (prod) | — |
| Frontend | React | 18.2.0 |
| Routing | React Router | v6.22.1 |
| HTTP Client | Axios | 1.6.7 |
| Styling | Tailwind CSS | 3.4.1 |
| Build Tool | Vite | 5.1.4 |
| Auth | JWT HS256 + HTTP-only cookies | python-jose 3.3.0 |
| Password Hashing | bcrypt | 4.2.1 |
| Rate Limiting | slowapi | 0.1.9 |
| Migrations | Alembic | 1.13.1 |
| Tests | pytest + httpx | 8.1.1 / 0.27.0 |

---

## How to Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m alembic upgrade head
python seed.py
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Local URLs:

```
Frontend: http://localhost:5173
Backend:  http://127.0.0.1:8001
API Docs: http://127.0.0.1:8001/docs  (development only)
```

### Windows shortcut

Double-click `start.bat` to launch both servers simultaneously.

### Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Project Structure

```
atai-travel/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, rate limit, router registration
│   │   ├── config.py                # Pydantic settings (reads .env)
│   │   ├── database.py              # SQLAlchemy engine, SessionLocal, get_db
│   │   ├── core/
│   │   │   ├── security.py          # JWT create/decode, bcrypt, get_current_user
│   │   │   └── rate_limit.py        # slowapi limiter instance
│   │   ├── models/
│   │   │   ├── user.py              # User (tourist|partner|admin)
│   │   │   ├── partner.py           # Partner (agency|hotel|transport)
│   │   │   ├── package.py           # Package + PackageDate
│   │   │   ├── booking.py           # Booking + WaitingList
│   │   │   ├── trip.py              # Trip + TripMember
│   │   │   ├── travel_request.py    # TravelRequest + TravelOffer (RFQ)
│   │   │   ├── social.py            # Like, UserSkip, Match, Message, Review, Complaint
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── auth.py              # /api/auth/*
│   │   │   ├── users.py             # /api/users/*
│   │   │   ├── packages.py          # /api/packages/*
│   │   │   ├── bookings.py          # /api/bookings/*
│   │   │   ├── trips.py             # /api/trips/*
│   │   │   ├── partners.py          # /api/partners/*
│   │   │   ├── travel_requests.py   # /api/travel-requests/*
│   │   │   ├── admin.py             # /api/admin/*
│   │   │   └── __init__.py
│   │   └── schemas/                 # Pydantic request/response schemas
│   ├── alembic/
│   │   └── versions/                # 4 migration files
│   ├── tests/
│   │   ├── conftest.py              # Test DB, fixtures, _auth_headers helpers
│   │   ├── test_auth.py             # Cookie auth + rate limit tests
│   │   ├── test_bookings.py         # Race condition + ownership tests
│   │   ├── test_individual.py       # Matching + contact privacy tests
│   │   ├── test_travel_requests.py  # RFQ + offer acceptance tests
│   │   ├── test_waitlist.py         # Waitlist position tests
│   │   └── test_admin.py            # Commission + dashboard tests
│   ├── seed.py                      # Seeds demo data
│   ├── seed_individual_users.py     # Seeds additional test users
│   ├── requirements.txt
│   ├── .env                         # GITIGNORED — real secrets
│   └── .env.example                 # Template
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js            # Axios instance, withCredentials, 401 handler
│   │   ├── context/
│   │   │   └── AuthContext.jsx      # Auth state, login/register/logout, session restore
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── PackageCard.jsx
│   │   │   └── TripCard.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx / Register.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── Individual.jsx       # Like/skip matching flow
│   │   │   ├── Matching.jsx         # Mutual matches view
│   │   │   ├── Packages.jsx         # Catalog with filters
│   │   │   ├── PackageDetail.jsx
│   │   │   ├── Booking.jsx
│   │   │   ├── MyBookings.jsx
│   │   │   ├── Trips.jsx / TripDetail.jsx
│   │   │   ├── TravelRequestForm.jsx
│   │   │   ├── MyTravelRequests.jsx
│   │   │   ├── PartnerRequests.jsx
│   │   │   ├── BecomePartner.jsx
│   │   │   ├── PartnerDashboard.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   └── AIAssistant.jsx
│   │   ├── utils/
│   │   │   └── travelLabels.js
│   │   ├── App.jsx                  # Route definitions + AuthProvider wrapper
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js               # Port 5173, /api proxy → :8001
│   ├── tailwind.config.js           # Custom primary/accent colors
│   └── package.json
├── .gitignore                       # .env, *.db, __pycache__, node_modules, dist
├── CLAUDE.md                        # Developer reference
├── About_project.md                 # This file
└── start.bat                        # Windows launcher
```

---

## User Roles

### Guest

Guests can:

- Open the homepage.
- View public package pages.
- Open the AI assistant page.
- Register or log in.

### Tourist

Tourists can:

- Update their profile and contact fields.
- Browse and book published tour packages.
- Create a custom travel request.
- Review offers from partners.
- Create and join group trips.
- Use individual matching.
- View incoming likes and respond with mutual interest.
- Access contacts only after a mutual match.
- Apply to become a partner.

### Partner

Partners can:

- Manage their partner dashboard.
- Create tour packages (submitted as `under_moderation`).
- View bookings for their packages.
- Confirm paid bookings for their own packages.
- View open tourist travel requests.
- Send package offers to tourists.

Partner accounts require admin approval before becoming active.

### Admin

Admins can:

- View platform dashboard metrics.
- Moderate users (warn, restrict, block).
- Approve or suspend partners.
- Approve or reject packages.
- Review and resolve complaints.
- Access partner-protected routes as an admin fallback.

---

## Authentication

JWT tokens are issued on login and registration. The backend sets the token in an HTTP-only cookie named `access_token`. The frontend restores the session by calling `GET /api/auth/me` on load.

**Token format:**
- Algorithm: HS256
- Subject (`sub`): `str(user_id)` — always a string
- Expiry: 24 hours (1440 minutes)
- Decoded with `int(payload.get("sub"))` to restore integer ID

**Cookie settings:**

| Environment | SameSite | Secure |
|---|---|---|
| development | Lax | False (HTTP allowed) |
| production | Strict | True (HTTPS required) |

**Auth resolution order in `get_current_user`:**
1. HTTP-only cookie `access_token` (preferred)
2. `Authorization: Bearer <token>` header (fallback for Swagger / API clients)

**Authorization levels:**
- `get_current_user` — any authenticated, non-blocked user
- `require_partner` — role is `partner` or `admin`
- `require_admin` — role is `admin` only

**Rate limiting:** 5 requests per minute on `/api/auth/login` and `/api/auth/register`.

Auth endpoints:

```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
```

---

## Database Models

### User

```
id, email, password_hash, full_name, age, city, bio, photo_url
role: "tourist" | "partner" | "admin"
status: "active" | "verified" | "hidden" | "warned" | "restricted" | "blocked" | "deleted"
interests, travel_style, budget_min, budget_max, languages, complaint_count
phone, telegram, whatsapp, instagram  ← only visible in mutual matches
```

### Partner

```
id, user_id→User, company_name, legal_info
partner_type: "agency" | "hotel" | "transport"
status: "pending" | "active" | "suspended" | "terminated"
commission_rate: float (default 12.0%)
```

### Package

```
id, partner_id→Partner, title, description, destination, region
price, duration_days, min_group_size, max_group_size
inclusions (JSON), exclusions (JSON), itinerary (JSON)
cancellation_policy, difficulty, travel_style
family_friendly, family_rates_enabled, featured
status: "draft" | "under_moderation" | "published" | "archived" | "suspended"
```

### PackageDate

```
id, package_id→Package, start_date
total_slots, available_slots
status: "available" | "full" | "past"
```

### Booking

```
id, user_id→User, package_id→Package, package_date_id→PackageDate
num_travelers, is_family_booking, family_discount_pct, base_price, total_price
expires_at (24h), paid_at, confirmed_at, cancellation_reason
status: "pending_payment" | "paid" | "pending_confirmation" | "confirmed"
        "cancelled_by_user" | "cancelled_by_partner" | "completed" | "expired"
        "disputed" | "resolved"
```

### WaitingList

```
id, user_id→User, package_date_id→PackageDate
position (assigned MAX(position)+1, not COUNT+1)
status: "waiting" | "offered" | "accepted" | "expired"
```

### Trip + TripMember

```
Trip:   id, organizer_id→User, title, destination, start_date, end_date
        min_size, max_size, current_size, budget_min, budget_max, travel_style
        status: "open" | "group_formed" | "active" | "completed" | "cancelled" | "emergency"

TripMember: id, trip_id→Trip, user_id→User
            status: "pending" | "accepted" | "rejected"
```

### TravelRequest + TravelOffer (RFQ)

```
TravelRequest: id, user_id→User
               origin, days, companions, interests (JSON), travel_format
               mood, difficulty, budget, season, accommodation, transport
               activities (JSON), preferred_places (JSON), distance, priority, notes
               status: "open" | "matched" | "closed"

TravelOffer: id, request_id→TravelRequest, partner_id→Partner
             title, description, price_total, price_per_person, duration_days
             included, message
             status: "submitted" | "accepted" | "declined"
```

### Social Models

```
Like:       id, from_user_id→User, to_user_id→User         (unique constraint)
UserSkip:   id, from_user_id→User, to_user_id→User         (unique constraint)
Match:      id, user1_id→User, user2_id→User               (user1_id = min of the two IDs)
Message:    id, match_id→Match, sender_id→User, content
Review:     id, user_id, package_id, booking_id (unique), rating, text, status
Complaint:  id, reporter_id→User, target_user_id→User, reason, description, status
```

---

## API Endpoints

### Authentication `/api/auth`

```
POST /register      — rate limited 5/min; sets HTTP-only cookie; age >= 18 required
POST /login         — rate limited 5/min; sets HTTP-only cookie; checks user not blocked
GET  /me            — restore session from cookie
POST /logout        — clears cookie
```

### Users & Matching `/api/users`

```
GET  /me                     — own profile with contact fields
PUT  /me                     — update profile
GET  /individual             — up to 20 candidates (excludes liked/skipped/self/admins/partners)
GET  /                       — browse all users with filters (max 50)
GET  /{id}                   — public profile (contacts hidden)
POST /{id}/like              — like user; returns {matched, contact_unlocked}
POST /{id}/skip              — skip (removes from /individual permanently)
GET  /me/matches             — mutual matches with contacts visible
GET  /me/incoming-likes      — users who liked you (contacts hidden until match)
POST /{id}/report            — file a complaint against user
```

### Packages `/api/packages`

```
GET  /              — list published packages (filters: destination, style, difficulty, price, family_friendly, featured)
GET  /{id}          — package detail with dates
POST /              — create package (partner only; starts as "under_moderation")
PUT  /{id}          — update own package (partner only)
```

### Bookings `/api/bookings`

```
POST /                      — create booking (atomic slot decrement)
POST /{id}/pay              — mock payment: pending_payment → paid
POST /{id}/confirm          — partner/admin: paid → confirmed (partner must own package)
POST /{id}/cancel           — cancel and restore slot
GET  /me                    — list user's bookings
POST /{date_id}/waitlist    — join waiting list (position = MAX+1)
```

### Trips `/api/trips`

```
GET  /                          — list open/group_formed trips
GET  /{id}                      — trip detail with members
POST /                          — create trip (organizer auto-added as "accepted")
POST /{id}/join                 — request to join (status="pending")
POST /{id}/members/{uid}/accept — organizer accepts member; current_size++
```

### Partners `/api/partners`

```
POST /apply             — apply for partner status (creates Partner, status="pending")
GET  /me/packages       — list partner's packages
GET  /me/bookings       — list bookings across partner's packages
GET  /me/stats          — total packages, bookings, GMV, commission, payout
```

### Travel Requests (RFQ) `/api/travel-requests`

```
POST /                          — create travel request (tourist)
GET  /me                        — own requests with received offers
GET  /open                      — all open requests (partner view)
POST /{req_id}/offers           — submit offer (partner; one per partner per request)
PUT  /offers/{offer_id}/accept  — accept offer; request → "matched"; others → "declined"
```

### Admin `/api/admin`

```
GET  /dashboard                     — platform metrics (SQL-aggregated)
GET  /users                         — all users
PUT  /users/{id}/status             — warn / restrict / block
GET  /partners                      — all partners
PUT  /partners/{id}/approve         — activate partner + set user.role="partner"
PUT  /partners/{id}/suspend         — suspend partner
GET  /packages/pending              — packages under moderation
PUT  /packages/{id}/approve         — publish package
PUT  /packages/{id}/reject          — archive package
GET  /complaints                    — pending complaints
PUT  /complaints/{id}/resolve       — dismiss / warn / block
```

---

## Core Business Logic

### Booking Flow

1. Tourist books a date → `pending_payment`, `expires_at = now + 24h`
2. Tourist pays → `paid`
3. Partner (or admin) confirms → `confirmed`
4. Post-trip → `completed`

**Atomic slot reservation (prevents race conditions):**

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

**Family discounts** (only if `family_rates_enabled`):
- 2–3 travelers → 20% off
- 4+ travelers → 30% off

### Commission Calculation

Uses SQL aggregation — never a hardcoded 12%:

```python
func.sum(Booking.total_price * Partner.commission_rate / 100)
# joined: Booking → Package → Partner
```

- `gmv` = sum of confirmed/completed booking totals
- `commission` = gmv × partner.commission_rate / 100
- `payout` = gmv − commission

### Matching System

1. User A likes User B → `Like` record created
2. User B likes User A → mutual like detected → `Match` created
3. Match unlocks contacts (phone, telegram, whatsapp, instagram)
4. Skip removes user from `/individual` permanently (idempotent)
5. Contacts never exposed in `UserPublic`; only in `UserMe` and `Match` responses

### Travel Request (RFQ) Flow

1. Tourist posts `TravelRequest` → status `"open"`
2. Partners view at `GET /travel-requests/open`
3. Partner submits offer (one per partner per request)
4. Tourist accepts one offer → request becomes `"matched"`, all other offers become `"declined"`

### Trip Organization

1. Organizer creates trip → auto-added as `"accepted"` member
2. Others join → `TripMember` status=`"pending"`
3. Organizer accepts members → `current_size++`
4. `current_size >= min_size` → trip status becomes `"group_formed"`

### Complaint & Moderation

Admin resolves with one of three actions:
- `dismiss` → no change
- `warn` → `complaint_count++`; if ≥3 → `"restricted"`, if ≥5 → `"blocked"`
- `block` → status=`"blocked"` immediately

### Waiting List Position

Uses `MAX(position) + 1` to avoid gaps that would cause duplicates when earlier entries are removed. Not `COUNT + 1`.

---

## Frontend Routes

Public:

```
/                   Home
/ai-assistant       AI assistant
/login
/register
/packages           Package catalog with filters
/packages/:id       Package detail
```

Authenticated (tourist):

```
/packages/:id/book  Booking flow (fetches package via API, works on refresh)
/trips              Trip discovery + create
/trips/:id          Trip detail + member management
/individual         Like/skip matching flow
/matching           Mutual matches with contacts
/profile            Edit profile
/my-bookings        User's bookings
/travel-request     Create travel request
/my-requests        Own requests + received offers
/become-partner     Partner application
```

Partner only:

```
/partner            Dashboard (stats, packages, bookings)
/partner/requests   View open RFQs + submit offers
```

Admin only:

```
/admin              Admin panel
```

---

## Test Coverage

57+ tests across 6 modules:

| Module | Tests | What it covers |
|---|---|---|
| `test_auth.py` | 11 | Cookie auth, session restore, bearer fallback, rate limiting, blocked users |
| `test_bookings.py` | 10 | Race condition (concurrent last slot), partner ownership check, family discount |
| `test_individual.py` | 20 | Matching candidates, mutual match, contact privacy, skip idempotency |
| `test_travel_requests.py` | 4 | RFQ create, offer submit, accept flow, ownership check |
| `test_waitlist.py` | 7 | Position uniqueness, MAX+1 logic, duplicate join rejected |
| `test_admin.py` | 5 | Per-partner commission rate, SQL aggregation, non-admin rejection |

Test infrastructure (`conftest.py`):
- Isolated SQLite DB per test (create_all / drop_all)
- `app.dependency_overrides[get_db]` redirects to test DB
- Fixtures: `tourist`, `tourist2`, `partner`, `partner2`, `admin`, `package`, `pkg_date`
- `_auth_headers(client, email, password)` helper for authenticated requests
- Rate limiter reset fixture between auth tests

---

## Alembic Migrations

Migration files in `backend/alembic/versions/`:

| Migration | Description |
|---|---|
| `3b8e04439b2f_initial.py` | Initial schema skeleton |
| `8d3a2b7f4c1e_travel_requests.py` | TravelRequest + TravelOffer tables |
| `c9f2e1a4b3d7_unique_constraints_likes_matches.py` | Unique constraints on Like, Match |
| `d4f1e2b3c8a9_individual_matching.py` | UserSkip + Match tables |

- Development: `create_all()` runs on startup
- Production: `alembic upgrade head` must run before deployment

---

## Security Measures

| Measure | Implementation |
|---|---|
| Password hashing | bcrypt (no plaintext) |
| Token theft prevention | HTTP-only cookies |
| HTTPS enforcement | `Secure=True` in production |
| CSRF protection | `SameSite=Strict` in production |
| CORS restriction | Explicit: localhost:5173 and :3000 only |
| Auth abuse prevention | Rate limit: 5/min on login + register |
| API docs exposure | `/docs` disabled in production |
| Race condition | Atomic `UPDATE WHERE available_slots > 0` |
| Privilege escalation | Role check on every protected endpoint |
| Partner ownership | Partner can only confirm their own packages |
| Contact privacy | Contacts only after mutual match |
| User moderation | Blocked users rejected even with valid token |

---

## Environment Configuration

Backend `.env`:

```env
SECRET_KEY=replace-with-64-char-random-hex
DATABASE_URL=sqlite:///./atai_travel.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
```

Frontend `.env` (optional):

```env
VITE_API_URL=http://127.0.0.1:8001
VITE_AI_ASSISTANT_URL=https://think-with-me-bot.lovable.app
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8001`.

---

## Demo Accounts (seeded by `seed.py`)

| Role | Email | Password |
|---|---|---|
| Admin | admin@atai.kg | admin123 |
| Partner | partner@nomad.kg | partner123 |
| Tourist | aizat@mail.kg | user123 |
| Tourist | temirlan@mail.kg | user123 |
| Tourist | sarah@gmail.com | user123 |

---

## AI Assistant

The site has a public AI assistant page at `/ai-assistant`. It opens an external URL configured via `VITE_AI_ASSISTANT_URL` (defaults to `https://think-with-me-bot.lovable.app`). The assistant can help with route selection, season advice, budget planning, rest ideas, and hiking preparation. No frontend secrets are exposed.

---

## MVP Strengths

- Clear separation between frontend and backend.
- Role-based user flows for tourist, partner, and admin.
- HTTP-only cookie auth instead of localStorage token storage.
- Rate limiting on auth routes.
- API docs hidden in production.
- Travel request and offer flow creates a useful marketplace loop.
- Individual matching keeps contacts private until mutual match.
- Backend has a meaningful pytest suite covering race conditions, ownership, and commission math.
- Atomic SQL update prevents slot double-booking under concurrency.
- Per-partner commission rates with SQL aggregation in admin dashboard.

---

## Known Limitations and Remaining Work

### Critical before production

- [ ] **Migrate SQLite → PostgreSQL** (SQLite not suitable for concurrent production traffic)
- [ ] Fix `database.py` to remove SQLite-specific `connect_args`
- [ ] Rate limiting is in-memory (should use Redis for multi-process production)
- [ ] **Initial Alembic migration** may not fully reflect all current tables for a fresh database

### Business logic gaps

- [ ] Waiting list auto-promotion on booking cancellation (currently manual)
- [ ] Expired unpaid bookings do not auto-restore slot inventory
- [ ] Booking slot decrement should account for `num_travelers`, not always 1
- [ ] Partner package update should not allow bypassing moderation status rules
- [ ] Add `POST /api/bookings/{id}/dispute` endpoint

### Missing features

- [ ] Password reset flow
- [ ] Email verification
- [ ] Transactional email notifications (booking, match, offer alerts)
- [ ] Real payment gateway integration (current flow is mocked)
- [ ] Image upload (currently uses external photo URLs)
- [ ] Password complexity rules (only min 6 chars enforced on frontend)
- [ ] `lang="ru"` and SEO meta tags in `index.html`
- [ ] React Error Boundary in `App.jsx`

### Testing and deployment

- [ ] Frontend unit tests (Vitest + React Testing Library)
- [ ] E2E tests (Playwright) for booking, matching, and partner flows
- [ ] Pagination on list endpoints (packages, users, bookings, admin)
- [ ] Docker setup + CI pipeline
- [ ] Production CORS origins (currently hardcoded to localhost)

---

## Completed Improvements

### Patch 1 (2026-04-25)

- [x] SECRET_KEY required from `.env`, no hardcoded default
- [x] JWT sub encoded as `str(user.id)`, decoded with `int()`
- [x] Booking race condition → atomic UPDATE WHERE available_slots > 0
- [x] Partner ownership check on booking confirm
- [x] Admin commission uses per-partner `commission_rate`
- [x] Admin dashboard uses SQL aggregation (not Python `.all()` iteration)
- [x] `.gitignore` covers `.env`, `*.db`, `__pycache__`
- [x] 16 backend tests covering all above

### Patch 2 (2026-04-25)

- [x] HTTP-only cookie auth (no more localStorage)
- [x] Rate limiting on `/api/auth/login` and `/register` (5/min)
- [x] `/docs` hidden in production (`ENVIRONMENT=production`)
- [x] CORS narrowed with explicit methods and headers
- [x] `create_all` removed from production startup
- [x] Alembic initialized, initial migration generated
- [x] Waitlist position uses `MAX+1` (not `count+1`)
- [x] `Booking.jsx` fetches package from API (works on refresh and direct URL)
- [x] Client-side form validation on booking form
