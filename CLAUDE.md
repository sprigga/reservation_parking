# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a community parking space reservation system (社區公共車位預約系統) built for managing parking spot bookings with time conflict prevention. The system allows residents to reserve parking spots and includes admin functionality for spot and reservation management.

**Tech Stack:**
- Backend: FastAPI + SQLAlchemy + SQLite 
- Frontend: Vue 3 + Vite + Axios
- Deployment: Docker Compose

## Development Commands

### Docker Environment (Primary)
```bash
# Start all services
docker compose up -d --build

# View logs
docker compose logs -f backend frontend db

# Restart specific service
docker compose restart backend
docker compose restart frontend

# Stop all services
docker compose down

# Clean rebuild with data reset
docker compose down -v && docker compose up -d --build
```

### Local Development (Alternative)
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview production build
```

### Testing & Verification
```bash
# Health check
curl http://localhost:8000/health

# Test admin login
curl -X POST http://localhost:8000/auth/login \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=admin&password=admin123'

# Check database (SQLite) - using specific container name
docker exec -it rp_backend sqlite3 /app/reservation_parking.db "SELECT name FROM sqlite_master WHERE type='table'; SELECT * FROM parking_spots;"

# Debug container logs
docker compose logs -f rp_backend rp_frontend
```

## Architecture

### Backend Structure (`backend/app/`)
- `main.py`: FastAPI app initialization, CORS, startup admin creation
- `api.py`: All API routes (auth, spots, reservations) with overlap validation
- `auth.py`: JWT authentication, password hashing, admin authorization
- `models.py`: SQLAlchemy models (User, ParkingSpot, Reservation)
- `schemas.py`: Pydantic models for request/response validation
- `database.py`: Database connection and session management

### Frontend Structure (`frontend/src/`)
- `App.vue`: Main layout with reservation form and admin sections
- `pages/ReservationForm.vue`: Public booking interface with time validation
- `pages/Admin.vue`: Admin login, spot management, reservation cancellation
- `api.js`: Axios client with automatic JWT token handling
- `auth.js`: Token storage and authentication state management

### Key Business Logic
**Time Overlap Prevention**: Implemented in backend (`api.py`) using condition:
```sql
(new_start < existing_end) AND (new_end > existing_start)
```

**Time Constraints**: 30-minute intervals, 24-hour format, auto-sync end date when start date changes

## Environment Configuration

**Required `.env` variables:**
```bash
SECRET_KEY=change-this-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
CORS_ORIGINS=http://localhost:5173
VITE_API_BASE=http://localhost:8000
TZ=Asia/Taipei
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

**Container names:**
- Backend: `rp_backend`
- Frontend: `rp_frontend`

**Default ports:**
- Frontend: 5173
- Backend: 8000

## Database Schema

- `users`: Authentication with admin flag
- `parking_spots`: Spot numbers with active/inactive status
- `reservations`: Bookings with name, household, phone, time range, linked to spots

Initial data includes spots A-01 through A-05, created automatically on startup.

## Common Issues & Solutions

1. **Backend bcrypt warnings**: Pin versions in `requirements.txt` (bcrypt==4.1.2, passlib==1.7.4)  
2. **Frontend Vite syntax errors**: Usually caused by invalid characters in source files, recreate affected files
3. **401 auto-logout**: Token expiry triggers automatic page reload, check/clear localStorage `rp_token`
4. **SQLite permission issues**: Ensure the backend container has write permissions to the SQLite database file

## Development Notes

- Admin operations require JWT authentication with `is_admin=True`
- All admin-protected endpoints use `Depends(require_admin)` 
- Frontend automatically includes Authorization header via Axios interceptors
- Database tables auto-created on backend startup
- Time picker uses 30-minute increments (00:00, 00:30, 01:00, etc.)
- End date auto-syncs when start date changes to prevent cross-day bookings