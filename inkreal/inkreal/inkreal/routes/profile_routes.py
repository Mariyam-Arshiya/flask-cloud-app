from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from firebase_config import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/<handle>")
def view(handle):
    db = get_db()
    users = list(db.collection("users").where("handle", "==", handle).limit(1).stream())
    if not users:
        flash("User not found.", "error")
        return redirect(url_for("main.feed"))
    user = users[0].to_dict()
    user_id = users[0].id
    user["id"] = user_id
    posts_ref = db.collection("posts").where("author_id", "==", user_id).where("status", "==", "published").order_by("created_at", direction="DESCENDING")
    posts = []
    for doc in posts_ref.stream():
        p = doc.to_dict()
        p["id"] = doc.id
        posts.append(p)
    dead_ends = [p for p in posts if p.get("post_type") == "dead_end"]
    is_following = False
    is_own = False
    if "user_id" in session:
        is_own = session["user_id"] == user_id
        if not is_own:
            is_following = session["user_id"] in user.get("followers", [])
    return render_template("profile.html", user=user, posts=posts, dead_ends=dead_ends,
                           is_following=is_following, is_own_profile=is_own)


@profile_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    user_doc = db.collection("users").document(session["user_id"]).get()
    if not user_doc.exists:
        session.clear()
        return redirect(url_for("auth.login"))
    user = user_doc.to_dict()
    user["id"] = session["user_id"]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        bio = request.form.get("bio", "").strip()
        website = request.form.get("website", "").strip()
        location = request.form.get("location", "").strip()
        avatar_url = request.form.get("avatar_url", "").strip()
        if not name:
            flash("Name is required.", "error")
            return render_template("settings.html", user=user)
        updates = {"name": name, "bio": bio, "website": website, "location": location, "avatar_letter": name[0].upper()}
        if avatar_url:
            updates["avatar_url"] = avatar_url
            session["user_avatar_url"] = avatar_url
        db.collection("users").document(session["user_id"]).update(updates)
        session["user_name"] = name
        session["user_avatar"] = name[0].upper()
        return redirect(url_for("profile.view", handle=user.get("handle")))
    return render_template("settings.html", user=user)
