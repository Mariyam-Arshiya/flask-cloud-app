from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from firebase_config import get_db
from datetime import datetime, timezone
import uuid

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.feed"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Please fill in all fields.", "error")
            return render_template("login.html")
        db = get_db()
        users_ref = db.collection("users").where("email", "==", email).limit(1)
        users = list(users_ref.stream())
        if not users:
            flash("No account found with this email.", "error")
            return render_template("login.html")
        user = users[0].to_dict()
        user_id = users[0].id
        from werkzeug.security import check_password_hash
        if not check_password_hash(user.get("password_hash", ""), password):
            flash("Incorrect password.", "error")
            return render_template("login.html")
        session["user_id"] = user_id
        session["user_name"] = user.get("name", "")
        session["user_handle"] = user.get("handle", "")
        session["user_avatar"] = user.get("avatar_letter", "")
        session["user_avatar_url"] = user.get("avatar_url", "")
        db.collection("users").document(user_id).update({"last_login": datetime.now(timezone.utc).isoformat()})
        return redirect(url_for("main.feed"))
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.feed"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        handle = request.form.get("handle", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        bio = request.form.get("bio", "").strip()
        if not all([name, handle, email, password]):
            flash("Please fill in all required fields.", "error")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")
        if len(handle) < 3:
            flash("Handle must be at least 3 characters.", "error")
            return render_template("register.html")
        import re
        if not re.match(r"^[a-z0-9_]+$", handle):
            flash("Handle can only contain lowercase letters, numbers, and underscores.", "error")
            return render_template("register.html")
        db = get_db()
        existing_email = list(db.collection("users").where("email", "==", email).limit(1).stream())
        if existing_email:
            flash("An account with this email already exists.", "error")
            return render_template("register.html")
        existing_handle = list(db.collection("users").where("handle", "==", handle).limit(1).stream())
        if existing_handle:
            flash("This handle is already taken.", "error")
            return render_template("register.html")
        from werkzeug.security import generate_password_hash
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        avatar_url = f"https://source.unsplash.com/200x200/?portrait,person&sig={user_id[:8]}"
        user_data = {
            "name": name, "handle": handle, "email": email,
            "password_hash": generate_password_hash(password),
            "bio": bio or "Human writer on InkReal.",
            "avatar_letter": name[0].upper(),
            "avatar_url": avatar_url,
            "cover_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1600&q=80",
            "created_at": now, "last_login": now,
            "followers": [], "following": [],
            "followers_count": 0, "following_count": 0, "post_count": 0,
            "streak_current": 0, "streak_longest": 0,
            "total_upvotes_received": 0, "verified_human": False,
            "website": "", "location": ""
        }
        db.collection("users").document(user_id).set(user_data)
        session["user_id"] = user_id
        session["user_name"] = name
        session["user_handle"] = handle
        session["user_avatar"] = name[0].upper()
        session["user_avatar_url"] = avatar_url
        flash("Welcome to InkReal. Start writing.", "success")
        return redirect(url_for("main.feed"))
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
