# 📄 ParkEase — Pages Guide & Prompt Reference

> **Version:** 1.0.0 | **Last Updated:** April 2026
> 
> This guide covers every page in the ParkEase app: its purpose, expected behavior, UI elements, route details, and AI/prompt guidance for generating or improving each page.

---

## Table of Contents

1. [Landing Page `/`](#1-landing-page-)
2. [Register Page `/register`](#2-register-page-register)
3. [Login Page `/login`](#3-login-page-login)
4. [User Dashboard `/dashboard`](#4-user-dashboard-dashboard)
5. [Slot Map & Reserve `/slots`](#5-slot-map--reserve-slots)
6. [Booking Confirmation `/booking/confirm`](#6-booking-confirmation-bookingconfirm)
7. [My Reservations `/reservations`](#7-my-reservations-reservations)
8. [Admin Dashboard `/admin`](#8-admin-dashboard-admin)
9. [Admin Slot Manager `/admin/slots`](#9-admin-slot-manager-adminslots)
10. [404 & Error Pages](#10-404--error-pages)
11. [AI Prompt Templates](#11-ai-prompt-templates)

---

## 1. Landing Page `/`

### Purpose
The public-facing homepage. Introduces the service, builds trust, and converts visitors into registered users.

### Route
```python
@app.route('/')
def index():
    return render_template('index.html')
```

### UI Elements

| Element          | Description                                                              |
|------------------|--------------------------------------------------------------------------|
| **Hero Banner**  | Headline: "Smart Parking, Simplified." + CTA buttons: Register / Login   |
| **Stats Bar**    | "500+ Slots · Available 24/7 · 3 Locations"                              |
| **How It Works** | 3-step cards: "Sign Up → Choose Slot → Drive In"                         |
| **Features List**| Icons + short descriptions of key features                               |
| **Footer**       | Links to Privacy Policy, Contact, Terms                                  |

### Expected Behavior
- If user is **already logged in**, redirect them to `/dashboard`
- CTA "Get Started" button → `/register`
- "Log In" button → `/login`

### Template: `templates/index.html`
```jinja2
{% extends 'base.html' %}
{% block content %}
<section class="hero">
  <h1>Smart Parking, Simplified.</h1>
  <p>Reserve your spot in seconds. No queues, no stress.</p>
  <a href="{{ url_for('auth.register') }}" class="btn btn-primary btn-lg">Get Started Free</a>
  <a href="{{ url_for('auth.login') }}" class="btn btn-outline btn-lg">Log In</a>
</section>
{% endblock %}
```

---

## 2. Register Page `/register`

### Purpose
New user account creation. Collects username, email, and password.

### Route
```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        # Validate → Hash password → Insert user → Redirect
    return render_template('auth/register.html')
```

### UI Elements

| Element            | Details                                              |
|--------------------|------------------------------------------------------|
| **Card**           | Centered, max-width 420px, shadow                    |
| **Username Field** | Required, min 3 chars, alphanumeric                  |
| **Email Field**    | Required, must be valid email format                 |
| **Password Field** | Required, min 8 chars, toggle show/hide              |
| **Submit Button**  | "Create Account" — primary button, full width        |
| **Login Link**     | "Already have an account? Log In" below the button   |
| **Error Messages** | Inline below each field for validation errors        |

### Validation Rules

```python
errors = {}

if len(username) < 3:
    errors['username'] = "Username must be at least 3 characters."

if '@' not in email:
    errors['email'] = "Please enter a valid email address."

if len(password) < 8:
    errors['password'] = "Password must be at least 8 characters."

if errors:
    return render_template('auth/register.html', errors=errors), 400
```

### Success Behavior
- On success: hash password with bcrypt, insert into DB, redirect to `/login` with flash message "Account created! Please log in."

---

## 3. Login Page `/login`

### Purpose
Authenticate returning users. Establish a session.

### Route
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password, user.password.encode('utf-8')):
            session['user_id'] = user.id
            session['role']    = user.role
            return redirect(url_for('user.dashboard'))
        flash("Invalid username or password.", "error")
    return render_template('auth/login.html')
```

### UI Elements

| Element             | Details                                           |
|---------------------|---------------------------------------------------|
| **Username Field**  | Auto-focus on page load                           |
| **Password Field**  | Show/hide toggle                                  |
| **Remember Me**     | Checkbox — sets `session.permanent = True`        |
| **Submit Button**   | "Log In" — primary, full width                    |
| **Error Banner**    | Red alert box above form for login failures       |
| **Register Link**   | "Don't have an account? Sign Up"                  |

### Success Behavior
- Admin users → `/admin`
- Regular users → `/dashboard`

---

## 4. User Dashboard `/dashboard`

### Purpose
The user's home base after login. Shows their active booking, stats, and recent reservation history.

### Route
```python
@login_required
@app.route('/dashboard')
def dashboard():
    user        = User.query.get(session['user_id'])
    active      = Reservation.query.filter_by(user_id=user.id, status='active').first()
    recent      = Reservation.query.filter_by(user_id=user.id).limit(5).all()
    total_count = Reservation.query.filter_by(user_id=user.id).count()
    return render_template('dashboard.html',
        user=user, active=active, recent=recent, total=total_count
    )
```

### UI Elements

| Zone                    | Details                                                           |
|-------------------------|-------------------------------------------------------------------|
| **Welcome Banner**      | "Good morning, [Name] 👋" — personalized greeting                 |
| **Stat Cards (row)**    | Active Bookings · Total All-Time · Hours Parked · Amount Spent    |
| **Active Booking Card** | Slot number, time remaining, Extend and Cancel buttons            |
| **Recent Reservations** | Table: Date, Slot, Duration, Cost, Status                         |
| **Quick Actions**       | "Reserve a Slot" and "View Full History" buttons                  |

### Empty State
If no active booking:
```html
<div class="empty-state">
  <img src="/static/img/empty-parking.svg" alt="">
  <h3>No Active Booking</h3>
  <p>You don't have an active reservation right now.</p>
  <a href="/slots" class="btn btn-primary">Find a Slot</a>
</div>
```

---

## 5. Slot Map & Reserve `/slots`

### Purpose
Browse all parking slots visually and make a reservation.

### Route
```python
@login_required
@app.route('/slots', methods=['GET', 'POST'])
def slots():
    slots = ParkingSlot.query.order_by(ParkingSlot.slot_number).all()
    return render_template('slots.html', slots=slots)
```

### UI Elements

| Zone                | Details                                                               |
|---------------------|-----------------------------------------------------------------------|
| **Floor Tabs**      | Tab bar to switch between Floor 1, 2, 3                               |
| **Slot Grid**       | Visual grid of colored slot tiles (green=available, red=booked)       |
| **Legend**          | Color key: Available / Booked / Your Booking / Maintenance            |
| **Side Panel**      | Appears when a slot is clicked: slot details + time picker + Reserve  |
| **Date/Time Input** | Start time + End time, min = now, auto-calculates cost                |
| **Cost Estimator**  | "Estimated cost: $X.XX" updates dynamically based on duration         |

### Slot Selection Behavior
```javascript
function selectSlot(slotId, status) {
    if (status === 'booked') return;   // Ignore clicks on booked slots
    // Highlight selected tile
    document.querySelectorAll('.slot-tile').forEach(t => t.classList.remove('selected'));
    document.getElementById('slot-' + slotId).classList.add('selected');
    // Show booking panel
    document.getElementById('booking-panel').classList.remove('hidden');
    document.getElementById('selected-slot-id').value = slotId;
}
```

### Reservation POST
```python
@app.route('/reserve', methods=['POST'])
@login_required
def reserve():
    slot_id    = request.form.get('slot_id')
    start_time = request.form.get('start_time')
    end_time   = request.form.get('end_time')
    # Validate slot is still available
    slot = ParkingSlot.query.get_or_404(slot_id)
    if slot.status == 'booked':
        flash("This slot was just taken. Please choose another.", "error")
        return redirect(url_for('slots'))
    # Create reservation
    reservation = Reservation(user_id=session['user_id'], slot_id=slot_id,
                               start_time=start_time, end_time=end_time, status='active')
    slot.status = 'booked'
    db.session.add(reservation)
    db.session.commit()
    return redirect(url_for('booking_confirm', reservation_id=reservation.id))
```

---

## 6. Booking Confirmation `/booking/confirm`

### Purpose
Show a successful booking confirmation. Reassure the user their spot is secured.

### Route
```python
@login_required
@app.route('/booking/confirm/<int:reservation_id>')
def booking_confirm(reservation_id):
    res  = Reservation.query.get_or_404(reservation_id)
    slot = ParkingSlot.query.get(res.slot_id)
    return render_template('booking_confirm.html', reservation=res, slot=slot)
```

### UI Elements

| Element                | Details                                            |
|------------------------|----------------------------------------------------|
| **Success Icon**       | Large green checkmark ✅                           |
| **Booking Summary**    | Slot number, floor, date, time, duration, cost     |
| **Booking Reference**  | Unique ID: `#RES-0042` in monospace font           |
| **Action Buttons**     | "Go to Dashboard" · "View All Reservations"        |
| **Print/Download**     | Optional print button for the confirmation ticket  |

---

## 7. My Reservations `/reservations`

### Purpose
Full history of user's past and current reservations.

### Route
```python
@login_required
@app.route('/reservations')
def my_reservations():
    page  = request.args.get('page', 1, type=int)
    items = Reservation.query.filter_by(user_id=session['user_id'])\
                .order_by(Reservation.created_at.desc())\
                .paginate(page=page, per_page=10)
    return render_template('reservations.html', reservations=items)
```

### UI Elements

| Element             | Details                                                     |
|---------------------|-------------------------------------------------------------|
| **Filter Bar**      | Filter by: Status (All / Active / Completed / Cancelled)    |
| **Reservations Table** | Columns: Date · Slot · Duration · Cost · Status · Actions |
| **Status Badges**   | Color-coded: Active (blue) / Completed (green) / Cancelled (gray)|
| **Cancel Button**   | Shown only for `active` reservations                        |
| **Pagination**      | Page controls at the bottom                                 |
| **Empty State**     | "No reservations yet. Book your first slot!"                |

---

## 8. Admin Dashboard `/admin`

### Purpose
Admin overview of the entire system — slots, users, revenue.

### Route
```python
@admin_required
@app.route('/admin')
def admin_dashboard():
    total_slots    = ParkingSlot.query.count()
    booked_slots   = ParkingSlot.query.filter_by(status='booked').count()
    total_users    = User.query.count()
    active_bookings = Reservation.query.filter_by(status='active').count()
    return render_template('admin/dashboard.html',
        total_slots=total_slots, booked_slots=booked_slots,
        total_users=total_users, active_bookings=active_bookings
    )
```

### UI Elements

| Zone              | Details                                                        |
|-------------------|----------------------------------------------------------------|
| **KPI Row**       | Total Slots · Booked · Available · Total Users · Active Now    |
| **Occupancy Bar** | Visual bar chart showing % occupancy by floor                  |
| **Live Feed**     | Last 10 reservations (auto-refresh every 30s)                  |
| **Quick Links**   | Manage Slots · Manage Users · View All Reservations            |

---

## 9. Admin Slot Manager `/admin/slots`

### Purpose
Create, edit, and change status of parking slots.

### Route
```python
@admin_required
@app.route('/admin/slots', methods=['GET', 'POST'])
def admin_slots():
    slots = ParkingSlot.query.order_by(ParkingSlot.slot_number).all()
    return render_template('admin/slots.html', slots=slots)

@admin_required
@app.route('/admin/slots/<int:slot_id>/toggle', methods=['POST'])
def toggle_slot(slot_id):
    slot = ParkingSlot.query.get_or_404(slot_id)
    slot.status = 'available' if slot.status == 'maintenance' else 'maintenance'
    db.session.commit()
    return jsonify({"status": slot.status})
```

### UI Elements

| Element              | Details                                                    |
|----------------------|------------------------------------------------------------|
| **Add Slot Form**    | Slot number, floor, type, price — inline form at top       |
| **Slots Table**      | All slots with inline status toggle buttons                |
| **Status Toggle**    | Switch between available / maintenance (no user actions)   |
| **Delete Button**    | With confirmation modal — disabled if slot has active bookings |
| **Bulk Actions**     | Select multiple → "Set Maintenance" or "Activate"          |

---

## 10. 404 & Error Pages

### 404 — Page Not Found
```python
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
```

Content:
- Friendly message: "We couldn't find that parking spot."
- Illustration of an empty parking lot
- "Go Back Home" button

### 500 — Server Error
```python
@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"500 error: {e}")
    return render_template('errors/500.html'), 500
```

Content:
- "Something went wrong on our end."
- Do NOT expose the traceback to users in production
- "Try Again" and "Home" buttons

---

## 11. AI Prompt Templates

Use these prompts with an AI assistant (like Claude) to generate, improve, or debug each page.

---

### 🏠 Landing Page Prompt
```
Build a professional landing page for a parking reservation web app called ParkEase.
Use Flask/Jinja2 with HTML, CSS, and vanilla JavaScript.
Include:
- A hero section with headline "Smart Parking, Simplified." and two CTA buttons: 
  "Get Started Free" (→ /register) and "Log In" (→ /login)
- A stats bar with 3 columns: "500+ Slots", "Available 24/7", "3 Locations"
- A "How It Works" section with 3 steps
- A features section with icons
- A footer with basic links
Use CSS variables for the color palette: primary #1A3C5E, accent #F97316, 
success #16A34A. Fonts: Sora for headings, Inter for body.
Make it mobile-responsive.
```

---

### 🔐 Register Page Prompt
```
Create a Flask user registration page for ParkEase parking app.
Requirements:
- Centered card layout (max-width: 420px) with shadow
- Form fields: Username (min 3 chars), Email (valid format), Password (min 8 chars, show/hide toggle)
- Inline validation error messages below each field (rendered from Flask flash messages)
- Full-width primary "Create Account" button
- Link: "Already have an account? Log In" linking to /login
- Handle POST: validate inputs, hash password with bcrypt, INSERT user, 
  redirect to /login with success flash
- On error: re-render form with error context, preserve username/email values
```

---

### 🅿️ Slot Map Page Prompt
```
Build a parking slot reservation page for ParkEase (Flask + Jinja2 + vanilla JS).
Features needed:
- A grid of colored square tiles representing parking slots
  (green = available, red = booked, blue = user's own booking)
- Each slot tile shows the slot number (e.g. "A-04") and is clickable if available
- Clicking an available slot opens a side panel with:
  - Slot details (number, floor, type, price/hr)
  - Start time and End time datetime-local inputs
  - A live cost estimate that updates based on duration selected
  - A "Reserve Now" button that POSTs to /reserve
- Floor tabs at the top to filter slots by floor
- A legend showing the color meanings
- All slots come from Jinja2 context variable `slots` (list of slot objects)
- Slots have properties: id, slot_number, status, floor, type, price_per_hour
```

---

### 📊 User Dashboard Prompt
```
Create a user dashboard page for ParkEase parking reservation app using Flask/Jinja2.
Layout: sidebar navigation on the left, main content area on the right.
Main content should include:
1. A personalized greeting: "Good [morning/afternoon/evening], [username] 👋"
2. A row of 4 stat cards: Active Bookings, Total Reservations, Hours Parked, Total Spent
3. An "Active Booking" card with slot number, time remaining (countdown), 
   and two buttons: "Extend" and "Cancel Booking"
   - If no active booking, show an empty state with an illustration and "Find a Slot" CTA
4. A recent reservations table (last 5): Date, Slot, Duration, Cost, Status
Flask context variables: user, active_reservation, recent_reservations, stats
```

---

### 🛠️ Admin Dashboard Prompt
```
Create an admin dashboard for ParkEase using Flask/Jinja2.
This page is only accessible to users with role='admin' (protected by @admin_required decorator).
Include:
1. A top stats row with 5 KPI cards: 
   Total Slots, Booked Now, Available, Total Users, Revenue Today
2. A slot occupancy bar chart (use a simple CSS/HTML bar chart or Chart.js)
3. A table of the 10 most recent reservations with columns: 
   Time, User, Slot, Duration, Status
4. Quick action buttons: "Add Slot", "View All Users", "Export Report"
Flask context: total_slots, booked_slots, total_users, today_revenue, recent_reservations
Admin sidebar navigation: Overview, Slot Manager, Users, Reservations, Settings
```

---

### 🐛 Debugging Prompt
```
I'm getting this error in my Flask parking app:
[PASTE YOUR ERROR HERE]

The relevant route code is:
[PASTE YOUR ROUTE CODE]

The relevant template code is:
[PASTE YOUR TEMPLATE CODE]

My database model is:
[PASTE YOUR MODEL]

Please:
1. Identify the root cause of the error
2. Provide a corrected version of the code
3. Explain why the error occurred
4. Suggest any related improvements to prevent similar issues
```

---

### ✨ Feature Addition Prompt
```
I have a Flask parking app (ParkEase) with the following existing structure:
[PASTE YOUR DIRECTORY STRUCTURE OR app.py]

I want to add the following feature:
[DESCRIBE THE FEATURE — e.g., "Email notifications when a booking is confirmed"]

Please provide:
1. The Flask route(s) needed
2. Any database schema changes (SQLite ALTER TABLE or new table)
3. The Jinja2 template changes needed
4. Any JavaScript changes for the frontend
5. Dependencies to install (if any)
Keep it consistent with the existing architecture and coding style.
```

---

*ParkEase Pages Guide — Reference this doc when building or modifying any page.*