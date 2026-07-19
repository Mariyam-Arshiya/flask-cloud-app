from flask import Blueprint, render_template, session, redirect, url_for
from firebase_config import get_db

community_bp = Blueprint("community", __name__)


@community_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    writers_ref = db.collection("users").order_by("dead_end_count", direction="DESCENDING").limit(20)
    writers = []
    for doc in writers_ref.stream():
        w = doc.to_dict()
        w["id"] = doc.id
        w.pop("password_hash", None)
        w.pop("email", None)
        writers.append(w)
    return render_template("community.html", writers=writers)
