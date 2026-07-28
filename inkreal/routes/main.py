from flask import Blueprint, render_template, session, redirect, url_for
from firebase_config import get_db

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

    db = get_db()
    posts_ref = db.collection("posts") \
        .where("status", "==", "published") \
        .order_by("created_at", direction="DESCENDING") \
        .limit(30)

    posts = []
    for doc in posts_ref.stream():
        post = doc.to_dict()
        post["id"] = doc.id
        posts.append(post)

    user_doc = db.collection("users").document(session["user_id"]).get()
    current_user = user_doc.to_dict() if user_doc.exists else {}
    current_user["id"] = session["user_id"]

    return render_template("feed.html", posts=posts, current_user=current_user)


@main_bp.route("/explore")
def explore():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_db()

    trending_ref = db.collection("posts") \
        .where("status", "==", "published") \
        .order_by("upvotes", direction="DESCENDING") \
        .limit(20)

    trending = []
    for doc in trending_ref.stream():
        post = doc.to_dict()
        post["id"] = doc.id
        trending.append(post)

    topics = [
        {"name": "Technology", "slug": "technology", "count": 0, "icon": "💻"},
        {"name": "Writing", "slug": "writing", "count": 0, "icon": "✍️"},
        {"name": "Life", "slug": "life", "count": 0, "icon": "🌿"},
        {"name": "Career", "slug": "career", "count": 0, "icon": "📈"},
        {"name": "Philosophy", "slug": "philosophy", "count": 0, "icon": "🤔"},
        {"name": "Creativity", "slug": "creativity", "count": 0, "icon": "🎨"},
        {"name": "Health", "slug": "health", "count": 0, "icon": "💪"},
        {"name": "Books", "slug": "books", "count": 0, "icon": "📚"},
        {"name": "Startups", "slug": "startups", "count": 0, "icon": "🚀"},
        {"name": "Design", "slug": "design", "count": 0, "icon": "🎯"},
    ]

    return render_template("explore.html", trending=trending, topics=topics)
