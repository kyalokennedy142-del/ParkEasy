# 🏗️ ParkEase — System Architecture

> **Version:** 1.0.0 | **Last Updated:** April 2026 | **Status:** Production

---

## Table of Contents

1. [Overview](#overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Directory Structure](#directory-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Schema](#database-schema)
7. [Authentication Flow](#authentication-flow)
8. [Request-Response Lifecycle](#request-response-lifecycle)
9. [Session Management](#session-management)
10. [Scalability Considerations](#scalability-considerations)

---

## Overview

ParkEase is a full-stack web application built on a **monolithic MVC architecture**, enabling users to search, reserve, and manage parking slots. It uses a lightweight Python/Flask backend with an SQLite database and a vanilla HTML/CSS/JS frontend.

```
Client (Browser)
      │
      ▼
 Flask Server  ◄──► SQLite Database
      │
      ▼
 HTML Templates (Jinja2)
```

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│   Browser → HTML/CSS/JS → Jinja2 Templates → AJAX Calls     │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP Requests
┌───────────────────────────▼──────────────────────────────────┐
│                     APPLICATION LAYER                        │
│                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   │
│  │   Routes    │   │  Middleware  │   │   Auth Guards   │   │
│  │  (app.py)   │──▶│  (sessions) │──▶│ (@login_required│   │
│  └─────────────┘   └─────────────┘   └─────────────────┘   │
│         │                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               Business Logic Layer                  │    │
│  │  UserService │ SlotService │ ReservationService     │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────┬──────────────────────────────────┘
                            │ SQL Queries
┌───────────────────────────▼──────────────────────────────────┐
│                       DATA LAYER                             │
│                                                              │
│   SQLite DB ──▶ parking.db                                   │
│   Tables: users │ parking_slots │ reservations               │
└──────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
parking-app/
│
├── app.py                    # Main application entry point
├── config.py                 # Configuration (dev/prod/test)
├── requirements.txt          # Python dependencies
├── parking.db                # SQLite database (auto-generated)
│
├── models/
│   ├── __init__.py
│   ├── user.py               # User model & queries
│   ├── slot.py               # Parking slot model & queries
│   └── reservation.py        # Reservation model & queries
│
├── routes/
│   ├── __init__.py
│   ├── auth.py               # /register, /login, /logout
│   ├── dashboard.py          # /dashboard
│   ├── slots.py              # /slots, /reserve, /cancel
│   └── admin.py              # /admin/*
│
├── static/
│   ├── css/
│   │   ├── base.css          # Global styles, CSS variables
│   │   ├── components.css    # Reusable UI components
│   │   └── pages/            # Page-specific styles
│   ├── js/
│   │   ├── main.js           # Global JS utilities
│   │   ├── dashboard.js      # Dashboard interactivity
│   │   └── admin.js          # Admin panel JS
│   └── img/
│       └── logo.svg
│
├── templates/
│   ├── base.html             # Base layout template
│   ├── index.html            # Landing / Home
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard.html        # User dashboard
│   ├── slots.html            # Slot selection map
│   └── admin/
│       ├── dashboard.html    # Admin overview
│       └── slots.html        # Slot management
│
└── tests/
    ├── test_auth.py
    ├── test_slots.py
    └── test_reservations.py
```

---

## Backend Architecture

### Framework: Flask (Python)

Flask follows a **route-handler** pattern. Each URL maps to a Python function.

```python
# app.py - Application Factory Pattern (recommended)
from flask import Flask
from models import db
from routes.auth import auth_bp
from routes.slots import slots_bp
from routes.admin import admin_bp

def create_app(config="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(slots_bp, url_prefix="/slots")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
```

### Blueprints

| Blueprint     | Prefix    | Responsibility                       |
|---------------|-----------|--------------------------------------|
| `auth_bp`     | `/auth`   | Registration, Login, Logout          |
| `slots_bp`    | `/slots`  | Viewing & reserving slots            |
| `admin_bp`    | `/admin`  | Admin management panel               |
| `user_bp`     | `/user`   | Profile, reservations history        |

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐          ┌─────────────────┐         ┌──────────────────┐
│    users     │          │  reservations   │         │  parking_slots   │
├──────────────┤          ├─────────────────┤         ├──────────────────┤
│ id (PK)      │◄────┐    │ id (PK)         │    ┌───▶│ id (PK)          │
│ username     │     └────│ user_id (FK)    │    │    │ slot_number      │
│ email        │          │ slot_id (FK)    │────┘    │ status           │
│ password     │          │ start_time      │         │ floor            │
│ role         │          │ end_time        │         │ type             │
│ created_at   │          │ status          │         │ price_per_hour   │
└──────────────┘          │ total_cost      │         └──────────────────┘
                          └─────────────────┘
```

### SQL Table Definitions

```sql
-- Users
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL UNIQUE,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,          -- bcrypt hashed
    role        TEXT DEFAULT 'user',    -- 'user' | 'admin'
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Parking Slots
CREATE TABLE parking_slots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_number   TEXT NOT NULL UNIQUE, -- e.g. "A-01", "B-12"
    status        TEXT DEFAULT 'available', -- 'available' | 'booked' | 'maintenance'
    floor         INTEGER DEFAULT 1,
    type          TEXT DEFAULT 'standard', -- 'standard' | 'disabled' | 'ev'
    price_per_hour REAL DEFAULT 2.50
);

-- Reservations
CREATE TABLE reservations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    slot_id     INTEGER NOT NULL,
    start_time  DATETIME NOT NULL,
    end_time    DATETIME NOT NULL,
    status      TEXT DEFAULT 'active', -- 'active' | 'completed' | 'cancelled'
    total_cost  REAL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
);
```

---

## Authentication Flow

```
User Submits Login Form
        │
        ▼
POST /auth/login
        │
        ▼
Validate Input Fields ──── FAIL ──▶ Return Error 400
        │
       PASS
        │
        ▼
Query DB for Username ──── NOT FOUND ──▶ Return Error 401
        │
       FOUND
        │
        ▼
bcrypt.checkpw(password, hash) ──── FAIL ──▶ Return Error 401
        │
       PASS
        │
        ▼
Set session['user_id'] = user.id
Set session['role'] = user.role
        │
        ▼
Redirect to /dashboard
```

---

## Request-Response Lifecycle

```
1. Browser sends HTTP Request
         │
         ▼
2. Flask URL Router matches endpoint
         │
         ▼
3. Middleware runs (session check, CSRF)
         │
         ▼
4. Route handler executes
   └── Calls model/service functions
   └── Queries SQLite via sql queries
         │
         ▼
5. Response assembled
   └── For pages: render_template() → Jinja2 HTML
   └── For API:   jsonify() → JSON response
         │
         ▼
6. HTTP Response returned to Browser
```

---

## Session Management

- Sessions stored **server-side** using Flask's signed cookie session.
- `SECRET_KEY` in `config.py` signs the cookie — keep this secret.
- Session expires after 30 minutes of inactivity (configurable).

```python
# config.py
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-me-in-production"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Enforce in production (HTTPS only)
```

---

## Scalability Considerations

| Current Limitation          | Recommended Migration Path               |
|-----------------------------|------------------------------------------|
| SQLite (single-file DB)     | PostgreSQL / MySQL for production        |
| Session-based auth          | JWT tokens for stateless/mobile clients  |
| Monolith Flask app          | Flask Blueprints → Microservices         |
| No caching                  | Redis for session store & slot caching   |
| Local file hosting          | Nginx + Gunicorn for production serving  |
| No background tasks         | Celery + Redis for booking expiry jobs   |

---

*ParkEase Architecture Documentation — Maintained by the Engineering Team*