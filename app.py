"""Agri-Waste Marketplace - Flask + PostgreSQL.
Separate farmer and buyer accounts (tables `farmers`, `buyers`), role-based dashboards."""
import os
import re
import time
from functools import wraps
import psycopg2
import psycopg2.extras
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, g, session, abort)
from werkzeug.security import generate_password_hash, check_password_hash

DB_CONFIG = dict(
    host=os.getenv("PGHOST", "localhost"),
    port=os.getenv("PGPORT", "5433"),   # 5433 = Docker database from docker-compose.yml
    dbname=os.getenv("PGDATABASE", "agri_marketplace"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", "Admin"),
)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")   # change before submission

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret")

TABLES = {"farmer": "farmers", "buyer": "buyers"}
WASTE_TYPES = {
    "Sugarcane bagasse": "Pulp plates, bowls and eco tableware",
    "Paddy straw": "Biobriquettes, mushroom beds, compost",
    "Rice husk": "Biobriquettes, boiler fuel",
    "Groundnut shells": "Biobriquettes (charcoal substitute)",
    "Cotton stalks": "Biobriquettes, particle board",
    "Maize cobs": "Biobriquettes, biogas",
    "Coconut shells and husk": "Charcoal, coir products",
    "Other": "Compost, biogas",
}
ICONS = {"Sugarcane bagasse": "🎋", "Paddy straw": "🌾", "Rice husk": "🍚", "Groundnut shells": "🥜",
         "Cotton stalks": "🌿", "Maize cobs": "🌽", "Coconut shells and husk": "🥥", "Other": "♻️"}
BUYER_TYPES = ["Pulp plate maker", "Biobriquette plant", "Compost maker",
               "Biogas plant", "Trader / other"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS farmers (
    id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL, village TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS buyers (
    id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL, company TEXT, buyer_type TEXT NOT NULL, password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS listings (
    id SERIAL PRIMARY KEY,
    farmer_name TEXT NOT NULL, phone TEXT NOT NULL, village TEXT NOT NULL,
    waste_type TEXT NOT NULL, quantity_kg DOUBLE PRECISION NOT NULL,
    price_per_kg DOUBLE PRECISION NOT NULL, available_from TEXT,
    description TEXT, status TEXT NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS inquiries (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    buyer_name TEXT NOT NULL, company TEXT, buyer_type TEXT NOT NULL,
    phone TEXT NOT NULL, message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE listings  ADD COLUMN IF NOT EXISTS farmer_id INTEGER REFERENCES farmers(id) ON DELETE SET NULL;
ALTER TABLE inquiries ADD COLUMN IF NOT EXISTS buyer_id  INTEGER REFERENCES buyers(id)  ON DELETE SET NULL;
"""

SAMPLE = [
    ("Sample Farmer 1", "9000000001", "Kavuluru", "Sugarcane bagasse", 5000, 2.5, "2026-07-20", "Fresh bagasse after juice crushing."),
    ("Sample Farmer 2", "9000000002", "Ibrahimpatnam", "Paddy straw", 8000, 1.2, "2026-08-01", "Dry straw, baled."),
    ("Sample Farmer 3", "9000000003", "Kavuluru", "Groundnut shells", 3000, 3.0, "2026-07-25", "Clean shells, no soil."),
]


# ---------- database helpers ----------
def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(**DB_CONFIG)
    return g.db


def query(sql, args=()):
    cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, args)
    return cur.fetchall()


def execute(sql, args=(), returning=False):
    cur = get_db().cursor()
    try:
        cur.execute(sql, args)
        row = cur.fetchone() if returning else None
        get_db().commit()
    except Exception:
        get_db().rollback()
        raise
    return row[0] if row else None


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = psycopg2.connect(**DB_CONFIG)
    cur = db.cursor()
    cur.execute(SCHEMA)
    cur.execute("SELECT COUNT(*) FROM listings")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO listings (farmer_name, phone, village, waste_type,"
                        " quantity_kg, price_per_kg, available_from, description)"
                        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", SAMPLE)
    db.commit()
    db.close()


def wait_for_db(tries=20):
    for attempt in range(tries):
        try:
            init_db()
            return
        except psycopg2.OperationalError as e:
            print(f"Waiting for database ({attempt + 1}/{tries}): {e}".strip())
            time.sleep(2)
    raise SystemExit("Could not connect to PostgreSQL. Is the database container running?")


# ---------- login helpers ----------
@app.context_processor
def inject_user():
    return dict(me_role=session.get("role"), me_name=session.get("name"), icons=ICONS)


def login_required(role):
    def deco(f):
        @wraps(f)
        def wrapper(*a, **k):
            if session.get("role") != role:
                flash(f"Please log in as a {role} to continue.", "error")
                return redirect(url_for("auth", mode="login", role=role))
            return f(*a, **k)
        return wrapper
    return deco


# ---------- public pages ----------
@app.route("/")
def index():
    return render_template("index.html", uses=WASTE_TYPES)


@app.route("/listings")
def listings():
    wtype = request.args.get("type", "")
    sql, args = "SELECT * FROM listings WHERE status='Available'", []
    if wtype in WASTE_TYPES:
        sql += " AND waste_type=%s"
        args.append(wtype)
    rows = query(sql + " ORDER BY id DESC", args)
    return render_template("listings.html", rows=rows, types=WASTE_TYPES, selected=wtype)


# ---------- signup / login / logout ----------
@app.route("/login/<role>", defaults={"mode": "login"}, methods=["GET", "POST"])
@app.route("/signup/<role>", defaults={"mode": "signup"}, methods=["GET", "POST"])
def auth(mode, role):
    if role not in TABLES:
        abort(404)
    f, table = request.form, TABLES[role]
    if request.method == "POST":
        email, pw = f.get("email", "").strip().lower(), f.get("password", "")
        if mode == "login":
            rows = query(f"SELECT * FROM {table} WHERE email=%s", (email,))
            if rows and check_password_hash(rows[0]["password_hash"], pw):
                session.clear()
                session.update(role=role, uid=rows[0]["id"], name=rows[0]["name"])
                return redirect(url_for("dashboard"))
            flash("Wrong email or password.", "error")
            return render_template("auth.html", mode=mode, role=role, form=f, buyer_types=BUYER_TYPES), 401
        phone, err = f.get("phone", "").strip(), None
        if not f.get("name", "").strip():
            err = "Enter your name."
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            err = "Enter a valid email address."
        elif not (phone.isdigit() and len(phone) == 10):
            err = "Enter a 10-digit phone number."
        elif len(pw) < 6:
            err = "Password must be at least 6 characters."
        elif pw != f.get("confirm"):
            err = "Passwords do not match."
        elif role == "farmer" and not f.get("village", "").strip():
            err = "Enter your village."
        elif role == "buyer" and f.get("buyer_type") not in BUYER_TYPES:
            err = "Choose what kind of buyer you are."
        elif query(f"SELECT 1 FROM {table} WHERE email=%s", (email,)):
            err = "This email is already registered. Please log in."
        if err:
            flash(err, "error")
            return render_template("auth.html", mode=mode, role=role, form=f, buyer_types=BUYER_TYPES), 400
        h = generate_password_hash(pw)
        if role == "farmer":
            uid = execute("INSERT INTO farmers (name,email,phone,village,password_hash)"
                          " VALUES (%s,%s,%s,%s,%s) RETURNING id",
                          (f["name"].strip(), email, phone, f["village"].strip(), h), True)
        else:
            uid = execute("INSERT INTO buyers (name,email,phone,company,buyer_type,password_hash)"
                          " VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                          (f["name"].strip(), email, phone, f.get("company", "").strip(),
                           f["buyer_type"], h), True)
        session.clear()
        session.update(role=role, uid=uid, name=f["name"].strip())
        flash("Account created. Welcome!", "ok")
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode=mode, role=role, form={}, buyer_types=BUYER_TYPES)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- dashboards ----------
@app.route("/dashboard")
def dashboard():
    role, uid = session.get("role"), session.get("uid")
    if role == "farmer":
        me = query("SELECT * FROM farmers WHERE id=%s", (uid,))[0]
        mine = query("SELECT l.*, (SELECT COUNT(*) FROM inquiries i WHERE i.listing_id=l.id) AS n"
                     " FROM listings l WHERE l.farmer_id=%s ORDER BY l.id DESC", (uid,))
        reqs = query("SELECT i.*, l.waste_type FROM inquiries i JOIN listings l ON l.id=i.listing_id"
                     " WHERE l.farmer_id=%s ORDER BY i.id DESC", (uid,))
        return render_template("farmer.html", me=me, mine=mine, reqs=reqs, types=WASTE_TYPES)
    if role == "buyer":
        me = query("SELECT * FROM buyers WHERE id=%s", (uid,))[0]
        sent = query("SELECT i.id, i.message, i.created_at, l.waste_type, l.quantity_kg, l.price_per_kg,"
                     " l.farmer_name, l.village, l.phone AS farmer_phone, l.status"
                     " FROM inquiries i JOIN listings l ON l.id=i.listing_id"
                     " WHERE i.buyer_id=%s ORDER BY i.id DESC", (uid,))
        return render_template("buyer.html", me=me, sent=sent)
    return redirect(url_for("auth", mode="login", role="farmer"))


@app.route("/listing/new", methods=["POST"])
@login_required("farmer")
def new_listing():
    f = request.form
    try:
        qty, price = float(f["quantity_kg"]), float(f["price_per_kg"])
    except (KeyError, ValueError):
        qty = price = -1
    if qty <= 0 or price < 0 or f.get("waste_type") not in WASTE_TYPES:
        flash("Enter a valid waste type, quantity above 0 and price.", "error")
        return redirect(url_for("dashboard"))
    me = query("SELECT * FROM farmers WHERE id=%s", (session["uid"],))[0]
    execute("INSERT INTO listings (farmer_id, farmer_name, phone, village, waste_type, quantity_kg,"
            " price_per_kg, available_from, description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (me["id"], me["name"], me["phone"], me["village"], f["waste_type"], qty, price,
             f.get("available_from") or None, f.get("description", "").strip()))
    flash("Listing published. Buyers can now send you requests.", "ok")
    return redirect(url_for("dashboard"))


@app.route("/listing/<int:lid>/<action>", methods=["POST"])
@login_required("farmer")
def listing_action(lid, action):
    if action == "sold":
        execute("UPDATE listings SET status='Sold' WHERE id=%s AND farmer_id=%s", (lid, session["uid"]))
    elif action == "delete":
        execute("DELETE FROM listings WHERE id=%s AND farmer_id=%s", (lid, session["uid"]))
    return redirect(url_for("dashboard"))


@app.route("/inquire/<int:lid>", methods=["POST"])
@login_required("buyer")
def inquire(lid):
    if not query("SELECT 1 FROM listings WHERE id=%s AND status='Available'", (lid,)):
        flash("This listing is no longer available.", "error")
        return redirect(url_for("listings"))
    b = query("SELECT * FROM buyers WHERE id=%s", (session["uid"],))[0]
    execute("INSERT INTO inquiries (listing_id, buyer_id, buyer_name, company, buyer_type, phone, message)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (lid, b["id"], b["name"], b["company"], b["buyer_type"], b["phone"],
             request.form.get("message", "").strip()))
    flash("Request sent. The farmer can now see your contact details.", "ok")
    return redirect(url_for("dashboard"))


# ---------- JSON API ----------
@app.route("/api/listings")
def api_listings():
    return jsonify(query("SELECT * FROM listings ORDER BY id DESC"))


@app.route("/api/stats")
def api_stats():
    by_type = query("SELECT waste_type, SUM(quantity_kg) AS kg, COUNT(*) AS n FROM listings"
                    " WHERE status='Available' GROUP BY waste_type ORDER BY kg DESC")
    totals = query("SELECT COUNT(*) AS listings, COALESCE(SUM(quantity_kg),0) AS kg FROM listings"
                   " WHERE status='Available'")[0]
    return jsonify(by_type=by_type, listings=totals["listings"], total_kg=totals["kg"],
                   farmers=query("SELECT COUNT(*) AS n FROM farmers")[0]["n"],
                   buyers=query("SELECT COUNT(*) AS n FROM buyers")[0]["n"],
                   inquiries=query("SELECT COUNT(*) AS n FROM inquiries")[0]["n"])


# ---------- admin ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
        else:
            flash("Wrong password.", "error")
        return redirect(url_for("admin"))
    if not session.get("admin"):
        return render_template("admin.html", authed=False)
    return render_template(
        "admin.html", authed=True,
        listings=query("SELECT * FROM listings ORDER BY id DESC"),
        inquiries=query("SELECT i.*, l.waste_type, l.farmer_name FROM inquiries i"
                        " JOIN listings l ON l.id=i.listing_id ORDER BY i.id DESC"),
        farmers=query("SELECT id,name,email,phone,village,created_at FROM farmers ORDER BY id DESC"),
        buyers=query("SELECT id,name,email,phone,company,buyer_type,created_at FROM buyers ORDER BY id DESC"))


@app.route("/admin/<action>/<int:listing_id>", methods=["POST"])
def admin_action(action, listing_id):
    if not session.get("admin"):
        return redirect(url_for("admin"))
    if action == "sold":
        execute("UPDATE listings SET status='Sold' WHERE id=%s", (listing_id,))
    elif action == "delete":
        execute("DELETE FROM listings WHERE id=%s", (listing_id,))
    return redirect(url_for("admin"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    wait_for_db()
    app.run(host=os.getenv("FLASK_HOST", "127.0.0.1"), port=5000,
            debug=os.getenv("FLASK_DEBUG", "1") == "1")
