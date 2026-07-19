from flask import Blueprint, render_template, session, redirect, url_for
from firebase_config import get_db, is_ready

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.feed"))
    return render_template("landing.html")


@main_bp.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if not is_ready():
        return redirect(url_for("main.setup_help"))
    db = get_db()
    posts_ref = db.collection("posts").where("status", "==", "published").order_by("created_at", direction="DESCENDING").limit(30)
    posts = []
    for doc in posts_ref.stream():
        post = doc.to_dict()
        post["id"] = doc.id
        posts.append(post)
    user_doc = db.collection("users").document(session["user_id"]).get()
    current_user = user_doc.to_dict() if user_doc.exists else {}
    current_user["id"] = session["user_id"]
    show_onboarding = not current_user.get("onboarded", False)
    return render_template("feed.html", posts=posts, current_user=current_user, show_onboarding=show_onboarding)


@main_bp.route("/explore")
def explore():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    dead_ends_ref = db.collection("posts").where("post_type", "==", "dead_end").where("status", "==", "published").order_by("created_at", direction="DESCENDING").limit(20)
    dead_ends = []
    for doc in dead_ends_ref.stream():
        p = doc.to_dict()
        p["id"] = doc.id
        dead_ends.append(p)
    trending_ref = db.collection("posts").where("status", "==", "published").order_by("likes", direction="DESCENDING").limit(15)
    trending = []
    for doc in trending_ref.stream():
        p = doc.to_dict()
        p["id"] = doc.id
        trending.append(p)
    tags = ["buildinpublic", "100DaysOfCode", "deadend", "iteration", "learning", "startups", "design", "writing"]
    return render_template("explore.html", dead_ends=dead_ends, trending=trending, tags=tags)


@main_bp.route("/tag/<tag>")
def tag_view(tag):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    posts_ref = db.collection("posts").where("tags", "array_contains", tag.lower()).where("status", "==", "published").order_by("created_at", direction="DESCENDING").limit(50)
    posts = []
    for doc in posts_ref.stream():
        p = doc.to_dict()
        p["id"] = doc.id
        posts.append(p)
    return render_template("tag.html", tag=tag, posts=posts)


@main_bp.route("/setup-help")
def setup_help():
    return render_template("setup_help.html")
