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
    posts_ref = db.collection("posts").where("status", "==", "published").order_by("created_at", direction="DESCENDING").limit(30)
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
    trending_ref = db.collection("posts").where("status", "==", "published").order_by("upvotes", direction="DESCENDING").limit(20)
    trending = []
    for doc in trending_ref.stream():
        post = doc.to_dict()
        post["id"] = doc.id
        trending.append(post)
    topics = [
        {"name": "Technology", "slug": "technology", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80"},
        {"name": "Writing", "slug": "writing", "image": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400&q=80"},
        {"name": "Life", "slug": "life", "image": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&q=80"},
        {"name": "Career", "slug": "career", "image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&q=80"},
        {"name": "Philosophy", "slug": "philosophy", "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&q=80"},
        {"name": "Creativity", "slug": "creativity", "image": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&q=80"},
        {"name": "Health", "slug": "health", "image": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400&q=80"},
        {"name": "Books", "slug": "books", "image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&q=80"},
        {"name": "Startups", "slug": "startups", "image": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&q=80"},
        {"name": "Design", "slug": "design", "image": "https://images.unsplash.com/photo-1561070791-2526d30994b8?w=400&q=80"},
    ]
    return render_template("explore.html", trending=trending, topics=topics)
