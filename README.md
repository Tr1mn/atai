# Atai Travel — MVP

Travel startup platform for Kyrgyzstan. Find companions, book packages, organize trips.

## Quick Start

```bash
# Option 1 — double-click start.bat

# Option 2 — manually:

# Backend
cd backend
pip install -r requirements.txt
python seed.py        # creates DB + demo data (run once)
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## URLs
- **Site**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@atai.kg | admin123 |
| Partner | partner@nomad.kg | partner123 |
| Tourist | aizat@mail.kg | user123 |

## Features
- Registration / Login (JWT)
- Package catalog with filters
- Booking flow with family discounts (BR-01)
- 24h payment timeout (BR-09), 48h confirmation timeout (BR-04)
- Waiting list when slots full
- Cancellation with refund policy (BR-03)
- Matching (like profiles → mutual like → match)
- Trips (create, join, organizer approval)
- Partner dashboard (packages, bookings, analytics)
- Admin panel (moderation, partners, complaints, packages)
