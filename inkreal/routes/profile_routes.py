from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from firebase_config import get_db
from utils.streak import calculate_streak, get_streak_level

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/<handle>")
def view(handle):
    db = get_db()

    users_ref = db.collection("users").where("handle", "==", handle).limit(1)
    users = list(users_ref.stream())

    if not users:
        flash("User not found.", "error")
        return redirect(url_for("main.feed"))

    user = users[0].to_dict()
    user_id = users[0].id
    user["id"] = user_id

    posts_ref = db.collection("posts") \
        .where("author_id", "==", user_id) \
        .where("status", "==", "published") \
        .order_by("created_at", direction="DESCENDING")

    posts = []
    post_dates = []
    for doc in posts_ref.stream():
        post = doc.to_dict()
        post["id"] = doc.id
        posts.append(post)
        post_dates.append(post.get("created_at"))

    streak_data = calculate_streak(post_dates)
    streak_level = get_streak_level(streak_data["current"])

    is_following = False
    is_own_profile = False
    if "user_id" in session:
        is_own_profile = session["user_id"] == user_id
        if not is_own_profile:
            is_following = session["user_id"] in user.get("followers", [])

    return render_template(
        "profile.html",
        user=user,
        posts=posts,
        streak=streak_data,
        streak_level=streak_level,
        is_following=is_following,
        is_own_profile=is_own_profile
    )


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

        if not name:
            flash("Name is required.", "error")
            return render_template("settings.html", user=user)

        update_data = {
            "name": name,
            "bio": bio,
            "website": website,
            "location": location,
            "avatar_letter": name[0].upper()
        }

        db.collection("users").document(session["user_id"]).update(update_data)
        session["user_name"] = name
        session["user_avatar"] = name[0].upper()

        flash("Profile updated.", "success")
        return redirect(url_for("profile.view", handle=user.get("handle")))

    return render_template("settings.html", user=user)
