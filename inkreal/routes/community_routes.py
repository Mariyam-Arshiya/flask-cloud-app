from flask import Blueprint, render_template, session, redirect, url_for
from firebase_config import get_db

community_bp = Blueprint("community", __name__)


@community_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_db()

    writers_ref = db.collection("users") \
        .order_by("streak_current", direction="DESCENDING") \
        .limit(20)

    writers = []
    for doc in writers_ref.stream():
        writer = doc.to_dict()
        writer["id"] = doc.id
        writer.pop("password_hash", None)
        writer.pop("email", None)
        writers.append(writer)

    return render_template("community.html", writers=writers)
