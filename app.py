from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, ParkingSlot, Booking
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

PARKING_LAYOUT = {
    "P01": {"zone": "North Wing", "row": "A", "distance": 1, "lat": -1.285830, "lng": 36.816510},
    "P02": {"zone": "North Wing", "row": "A", "distance": 2, "lat": -1.285840, "lng": 36.816730},
    "P03": {"zone": "North Wing", "row": "A", "distance": 3, "lat": -1.285850, "lng": 36.816950},
    "P04": {"zone": "North Wing", "row": "A", "distance": 4, "lat": -1.285860, "lng": 36.817170},
    "P05": {"zone": "North Wing", "row": "A", "distance": 5, "lat": -1.285870, "lng": 36.817390},
    "P06": {"zone": "South Wing", "row": "B", "distance": 6, "lat": -1.286180, "lng": 36.816510},
    "P07": {"zone": "South Wing", "row": "B", "distance": 7, "lat": -1.286190, "lng": 36.816730},
    "P08": {"zone": "South Wing", "row": "B", "distance": 8, "lat": -1.286200, "lng": 36.816950},
    "P09": {"zone": "South Wing", "row": "B", "distance": 9, "lat": -1.286210, "lng": 36.817170},
    "P10": {"zone": "South Wing", "row": "B", "distance": 10, "lat": -1.286220, "lng": 36.817390},
}


def build_slot_view(slot):
    layout = PARKING_LAYOUT.get(slot.slot_number, {})
    latest_booking = slot.bookings[-1] if slot.bookings else None
    return {
        "id": slot.id,
        "slot_number": slot.slot_number,
        "status": slot.status,
        "lat": layout.get("lat", app.config["PARKING_MAP_CENTER_LAT"]),
        "lng": layout.get("lng", app.config["PARKING_MAP_CENTER_LNG"]),
        "zone": layout.get("zone", "General Zone"),
        "row": layout.get("row", "-"),
        "distance": layout.get("distance", 999),
        "booked_by": latest_booking.user.username if latest_booking else None,
        "recommended": False,
    }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if ParkingSlot.query.count() == 0:
        for i in range(1, 11):
            db.session.add(ParkingSlot(slot_number=f"P{i:02d}"))
        db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("Username exists.")
            return redirect(url_for("register"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registered! Login now.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    slots = ParkingSlot.query.all()
    slot_views = sorted((build_slot_view(slot) for slot in slots), key=lambda item: item["slot_number"])
    available_slots = [slot for slot in slot_views if slot["status"] == "available"]
    recommended_slot = min(available_slots, key=lambda item: item["distance"], default=None)
    if recommended_slot:
        for slot in slot_views:
            slot["recommended"] = slot["id"] == recommended_slot["id"]
        for slot in available_slots:
            slot["recommended"] = slot["id"] == recommended_slot["id"]
    return render_template(
        "dashboard.html",
        slots=slot_views,
        available_slots=available_slots,
        recommended_slot=recommended_slot,
        parking_map_center={
            "lat": app.config["PARKING_MAP_CENTER_LAT"],
            "lng": app.config["PARKING_MAP_CENTER_LNG"],
        },
    )

@app.route("/pay/<int:slot_id>", methods=["POST"])
@login_required
def pay_for_slot(slot_id):
    slot = ParkingSlot.query.get_or_404(slot_id)
    if slot.status != "available":
        flash("Slot already booked.", "error")
        return redirect(url_for("dashboard"))

    # Simulate payment success
    slot.status = "booked"
    booking = Booking(
        user_id=current_user.id,
        slot_id=slot.id,
        payment_status="paid",
        amount=5.00
    )
    db.session.add(booking)
    db.session.commit()
    flash(f"Payment successful. Slot {slot.slot_number} booked for $5.00", "success")
    return redirect(url_for("dashboard"))

@app.route("/admin")
@login_required
def admin():
    if current_user.username != "admin":
        flash("Admin only.")
        return redirect(url_for("dashboard"))
    slots = sorted((build_slot_view(slot) for slot in ParkingSlot.query.all()), key=lambda item: item["slot_number"])
    return render_template("admin.html", slots=slots)

@app.route("/admin/reset/<int:slot_id>", methods=["POST"])
@login_required
def reset_slot(slot_id):
    if current_user.username != "admin":
        return redirect(url_for("dashboard"))
    slot = ParkingSlot.query.get_or_404(slot_id)
    slot.status = "available"
    db.session.commit()
    flash(f"Slot {slot.slot_number} reset to available.")
    return redirect(url_for("admin"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/bookings")
@login_required
def my_bookings():
    """User booking history"""
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
    return render_template("bookings.html", bookings=bookings)

@app.route("/receipt/<int:booking_id>")
@login_required
def view_receipt(booking_id):
    """Payment receipt view"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and current_user.username != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("dashboard"))
    return render_template("receipt.html", booking=booking)

@app.route("/admin/reports")
@login_required
def admin_reports():
    """Admin analytics & revenue simulation"""
    if current_user.username != "admin":
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard"))
    
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.amount)).scalar() or 0.0
    occupancy_rate = int((ParkingSlot.query.filter_by(status='booked').count() / ParkingSlot.query.count()) * 100) if ParkingSlot.query.count() else 0
    recent_bookings = Booking.query.order_by(Booking.booked_at.desc()).limit(10).all()
    
    return render_template("reports.html", 
                           total_bookings=total_bookings, 
                           total_revenue=total_revenue, 
                           occupancy_rate=occupancy_rate,
                           recent_bookings=recent_bookings)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
