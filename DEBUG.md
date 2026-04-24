# 🐛 ParkEase — Debugging Guide

> **Version:** 1.0.0 | **Last Updated:** April 2026

---

## Table of Contents

1. [Enable Debug Mode](#enable-debug-mode)
2. [Common Errors & Fixes](#common-errors--fixes)
3. [Database Debugging](#database-debugging)
4. [Authentication Issues](#authentication-issues)
5. [Route & Template Errors](#route--template-errors)
6. [Frontend Debugging](#frontend-debugging)
7. [Logging Setup](#logging-setup)
8. [Testing Your App](#testing-your-app)
9. [Environment Checklist](#environment-checklist)
10. [Debug Tools Reference](#debug-tools-reference)

---

## Enable Debug Mode

**Never run debug mode in production.** Use it locally only.

### Method 1 — Environment Variable (Recommended)

```bash
# Linux / macOS
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

```powershell
# Windows PowerShell
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = 1
python app.py
```

### Method 2 — In Code (dev only)

```python
# app.py
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

When debug mode is active you get:
- ✅ Auto-reload on file save
- ✅ Interactive browser debugger on exceptions
- ✅ Detailed tracebacks in terminal
- ⚠️ NEVER expose port 5000 publicly in this mode

---

## Common Errors & Fixes

### ❌ `ModuleNotFoundError: No module named 'flask'`

**Cause:** Flask is not installed or wrong Python environment is active.

```bash
# Fix 1 — Install Flask
pip install flask

# Fix 2 — Check you're using the right Python
which python         # macOS/Linux
where python         # Windows
python --version

# Fix 3 — Install all dependencies
pip install -r requirements.txt
```

---

### ❌ `OperationalError: no such table: users`

**Cause:** Database tables have not been created yet.

```python
# Fix — Add to app.py and run once
with app.app_context():
    db.create_all()
    print("✅ Tables created.")
```

Or via Flask shell:

```bash
flask shell
>>> from models import db
>>> db.create_all()
```

---

### ❌ `RuntimeError: Working outside of application context`

**Cause:** Accessing `db` or `session` outside a Flask request context.

```python
# ❌ Wrong — called at module level
users = User.query.all()

# ✅ Fix — wrap in app context
with app.app_context():
    users = User.query.all()
```

---

### ❌ `KeyError: 'user_id'` in session

**Cause:** Accessing `session['user_id']` before login sets it, or after session expires.

```python
# ❌ Wrong
user_id = session['user_id']

# ✅ Fix — use .get() with a default
user_id = session.get('user_id')
if not user_id:
    return redirect(url_for('auth.login'))
```

---

### ❌ `404 Not Found` on a route you defined

**Cause:** Route not registered (Blueprint not added to app, typo in URL, method mismatch).

**Checklist:**
```python
# 1. Print all registered routes
with app.app_context():
    print(app.url_map)

# 2. Check Blueprint is registered
app.register_blueprint(slots_bp, url_prefix="/slots")

# 3. Check methods
@app.route('/reserve', methods=['GET', 'POST'])  # must include POST if form submits
```

---

### ❌ `405 Method Not Allowed`

**Cause:** A form POSTs to a route that only allows GET.

```python
# Fix — Add POST to the allowed methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ...
```

---

### ❌ `Jinja2 UndefinedError: 'variable' is undefined`

**Cause:** Template uses a variable not passed in `render_template()`.

```python
# ❌ Wrong
return render_template('dashboard.html')

# ✅ Fix — pass all required variables
return render_template('dashboard.html', user=current_user, slots=slots)
```

Inside template, use safe default:

```jinja2
{{ user.username | default('Guest') }}
```

---

### ❌ `IntegrityError: UNIQUE constraint failed: users.username`

**Cause:** Trying to register a username/email that already exists.

```python
# Fix — check before inserting
from sqlite3 import IntegrityError

try:
    db.session.add(new_user)
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    flash("Username already taken. Please choose another.", "error")
```

---

### ❌ `CSRF Token Missing or Invalid`

**Cause:** Form submission missing CSRF protection token (if Flask-WTF is enabled).

```html
<!-- Add this inside every <form> -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

---

## Database Debugging

### Inspect the SQLite Database

```bash
# Open the DB via SQLite CLI
sqlite3 parking.db

# Useful commands inside sqlite3:
.tables                          -- List all tables
.schema users                    -- Show table structure
SELECT * FROM users;             -- View all users
SELECT * FROM parking_slots WHERE status='booked';
.exit
```

### Check for Locked Database

SQLite can lock if two processes access it simultaneously.

```bash
# Check if DB is locked by another process (Linux)
lsof parking.db

# Fix — kill the offending process or restart the app
```

### Reset the Database (Dev Only)

```bash
# Delete and recreate
rm parking.db
flask shell
>>> from models import db
>>> db.create_all()
>>> exit()
```

### Seed Test Data

```python
# scripts/seed.py
from app import create_app
from models import db, User, ParkingSlot
import bcrypt

app = create_app()

with app.app_context():
    # Admin user
    pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
    admin = User(username="admin", email="admin@parkease.com", password=pw, role="admin")
    db.session.add(admin)

    # Sample slots
    for i in range(1, 21):
        slot = ParkingSlot(slot_number=f"A-{i:02d}", status="available", floor=1)
        db.session.add(slot)

    db.session.commit()
    print("✅ Seed data inserted.")
```

```bash
python scripts/seed.py
```

---

## Authentication Issues

### User Can't Log In (Correct Password)

```python
# Verify bcrypt hash is being checked correctly
import bcrypt

stored_hash = user.password  # bytes from DB
entered_pw  = request.form['password'].encode('utf-8')

if bcrypt.checkpw(entered_pw, stored_hash):
    print("✅ Password correct")
else:
    print("❌ Password mismatch")
```

**Common Pitfall:** Storing password as a plain string instead of bytes.

```python
# ❌ Wrong
password = bcrypt.hashpw(plain_pw, bcrypt.gensalt())
user.password = password                      # stores bytes object

# ✅ Fix — decode to string for SQLite TEXT column
user.password = password.decode('utf-8')

# Then when checking:
bcrypt.checkpw(entered_pw, stored_hash.encode('utf-8'))
```

---

### Session Not Persisting Across Requests

```python
# Ensure SECRET_KEY is set and stable
app.secret_key = "your-stable-secret-key"

# ❌ Bad — random key changes on every restart
app.secret_key = os.urandom(24)
```

---

## Route & Template Errors

### Debugging a Specific Route

```python
@app.route('/dashboard')
def dashboard():
    print("=== DEBUG /dashboard ===")
    print(f"Session: {dict(session)}")
    print(f"User ID: {session.get('user_id')}")
    # ... rest of function
```

### Check Template Is Found

Flask looks for templates in `/templates/`. Ensure:
```
templates/
  base.html          ← exists
  dashboard.html     ← exists
  auth/
    login.html       ← correct subfolder
```

```python
# Template not found error — check render path
return render_template('auth/login.html')   # ✅ correct
return render_template('login.html')        # ❌ if in auth/ subfolder
```

---

## Frontend Debugging

### Browser DevTools Checklist

1. **Open DevTools:** `F12` or `Cmd+Option+I`
2. **Console tab:** Check for JavaScript errors
3. **Network tab:** Check for failing AJAX/fetch calls (status codes, payloads)
4. **Application tab → Cookies:** Inspect session cookie presence
5. **Elements tab:** Inspect CSS classes and computed styles

### Debug JavaScript

```javascript
// Add temporary debug logging
console.log("Slot clicked:", slotId);
console.table(slotsData);             // Pretty-print arrays/objects
console.error("Booking failed:", err); // Red error in console
```

### AJAX/Fetch Debugging

```javascript
fetch('/reserve', {
    method: 'POST',
    body: JSON.stringify({ slot_id: 3 }),
    headers: { 'Content-Type': 'application/json' }
})
.then(res => {
    console.log("Status:", res.status);
    return res.json();
})
.then(data => console.log("Response:", data))
.catch(err => console.error("Network error:", err));
```

---

## Logging Setup

Add structured logging to track errors in production:

```python
# config.py / app.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        handler = RotatingFileHandler(
            'logs/parkease.log',
            maxBytes=1_000_000,   # 1MB per file
            backupCount=5
        )
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
```

### Usage in Routes

```python
from flask import current_app

@app.route('/reserve', methods=['POST'])
def reserve():
    try:
        # ... booking logic
        current_app.logger.info(f"User {user_id} reserved slot {slot_id}")
    except Exception as e:
        current_app.logger.error(f"Reservation failed: {e}", exc_info=True)
        return jsonify({"error": "Reservation failed"}), 500
```

---

## Testing Your App

### Run Unit Tests

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

### Sample Auth Test

```python
# tests/test_auth.py
import pytest
from app import create_app
from models import db

@pytest.fixture
def client():
    app = create_app("config.TestingConfig")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register(client):
    res = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'SecurePass1!'
    })
    assert res.status_code in [200, 302]

def test_login_invalid(client):
    res = client.post('/auth/login', data={
        'username': 'nobody',
        'password': 'wrongpass'
    })
    assert b'Invalid' in res.data
```

---

## Environment Checklist

Before running the app, verify this checklist:

```
Pre-Run Checklist
─────────────────────────────────────────────
 [ ] Python 3.8+ installed         python --version
 [ ] Virtual environment active    source venv/bin/activate
 [ ] Dependencies installed        pip install -r requirements.txt
 [ ] .env file exists with:
       SECRET_KEY=<value>
       FLASK_ENV=development
 [ ] Database initialized          flask shell → db.create_all()
 [ ] Port 5000 is free             lsof -i :5000
 [ ] No syntax errors              python -m py_compile app.py
─────────────────────────────────────────────
```

---

## Debug Tools Reference

| Tool                | Purpose                              | Command / URL                        |
|---------------------|--------------------------------------|--------------------------------------|
| Flask Debug Mode    | Interactive exception browser        | `FLASK_DEBUG=1 python app.py`       |
| Flask Shell         | REPL with app context                | `flask shell`                        |
| SQLite CLI          | Inspect database directly            | `sqlite3 parking.db`                 |
| pytest              | Run unit/integration tests           | `pytest tests/ -v`                   |
| pytest-cov          | Test coverage report                 | `pytest --cov=. --cov-report=html`  |
| Browser DevTools    | Frontend inspection                  | F12 in browser                       |
| Python pdb          | Step-through Python debugger         | `import pdb; pdb.set_trace()`        |
| Flask-DebugToolbar  | In-browser debug panel               | `pip install flask-debugtoolbar`     |

---

*ParkEase Debug Guide — Keep this handy during development.*