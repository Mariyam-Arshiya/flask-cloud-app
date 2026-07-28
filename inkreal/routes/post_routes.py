from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from firebase_config import get_db
from utils.helpers import generate_slug, truncate_text
from utils.humancheck import analyze_human_score
from utils.streak import calculate_streak
from datetime import datetime, timezone
import uuid

post_bp = Blueprint("post", __name__)


@post_bp.route("/write", methods=["GET", "POST"])
def write():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        subtitle = request.form.get("subtitle", "").strip()
        topic = request.form.get("topic", "general").strip()
        post_type = request.form.get("post_type", "article")

        if not title or not content:
            flash("Title and content are required.", "error")
            return render_template("write.html")

        if len(content) < 50:
            flash("Write at least 50 characters. Express yourself!", "error")
            return render_template("write.html")

        db = get_db()
        user_doc = db.collection("users").document(session["user_id"]).get()
        user = user_doc.to_dict()

        human_analysis = analyze_human_score(content)

        post_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        slug = generate_slug(title)

        post_data = {
            "title": title,
            "subtitle": subtitle,
            "content": content,
            "excerpt": truncate_text(content, 200),
            "slug": slug,
            "topic": topic,
            "post_type": post_type,
            "author_id": session["user_id"],
            "author_name": user.get("name", ""),
            "author_handle": user.get("handle", ""),
            "author_avatar_letter": user.get("avatar_letter", "?"),
            "author_avatar_color": user.get("avatar_color", "#4111CC"),
            "created_at": now,
            "updated_at": now,
            "status": "published",
            "upvotes": 0,
            "upvoted_by": [],
            "bookmarks": 0,
            "bookmarked_by": [],
            "comment_count": 0,
            "view_count": 0,
            "human_score": human_analysis["score"],
            "human_label": human_analysis["label"],
            "word_count": len(content.split()),
            "featured": False
        }

        db.collection("posts").document(post_id).set(post_data)

        db.collection("users").document(session["user_id"]).update({
            "post_count": (user.get("post_count", 0) + 1)
        })

        posts_ref = db.collection("posts") \
            .where("author_id", "==", session["user_id"]) \
            .where("status", "==", "published") \
            .order_by("created_at", direction="DESCENDING")

        post_dates = [doc.to_dict().get("created_at") for doc in posts_ref.stream()]
        streak_data = calculate_streak(post_dates)

        db.collection("users").document(session["user_id"]).update({
            "streak_current": streak_data["current"],
            "streak_longest": max(
                streak_data["longest"],
                user.get("streak_longest", 0)
            )
        })

        flash("Published! Your words are out there.", "success")
        return redirect(url_for("post.view", post_id=post_id))

    return render_template("write.html")


@post_bp.route("/<post_id>")
def view(post_id):
    db = get_db()
    post_doc = db.collection("posts").document(post_id).get()

    if not post_doc.exists:
        flash("Post not found.", "error")
        return redirect(url_for("main.feed"))

    post = post_doc.to_dict()
    post["id"] = post_id

    db.collection("posts").document(post_id).update({
        "view_count": post.get("view_count", 0) + 1
    })

    comments_ref = db.collection("posts").document(post_id) \
        .collection("comments") \
        .order_by("created_at", direction="ASCENDING")

    comments = []
    for doc in comments_ref.stream():
        comment = doc.to_dict()
        comment["id"] = doc.id
        comments.append(comment)

    is_upvoted = False
    is_bookmarked = False
    if "user_id" in session:
        is_upvoted = session["user_id"] in post.get("upvoted_by", [])
        is_bookmarked = session["user_id"] in post.get("bookmarked_by", [])

    more_posts_ref = db.collection("posts") \
        .where("author_id", "==", post.get("author_id")) \
        .where("status", "==", "published") \
        .order_by("created_at", direction="DESCENDING") \
        .limit(4)

    more_posts = []
    for doc in more_posts_ref.stream():
        if doc.id != post_id:
            mp = doc.to_dict()
            mp["id"] = doc.id
            more_posts.append(mp)

    return render_template(
        "post_detail.html",
        post=post,
        comments=comments,
        is_upvoted=is_upvoted,
        is_bookmarked=is_bookmarked,
        more_posts=more_posts[:3]
    )


@post_bp.route("/<post_id>/delete", methods=["POST"])
def delete(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_db()
    post_doc = db.collection("posts").document(post_id).get()

    if not post_doc.exists:
        flash("Post not found.", "error")
        return redirect(url_for("main.feed"))

    post = post_doc.to_dict()
    if post.get("author_id") != session["user_id"]:
        flash("You can only delete your own posts.", "error")
        return redirect(url_for("main.feed"))

    db.collection("posts").document(post_id).delete()

    user_doc = db.collection("users").document(session["user_id"]).get()
    if user_doc.exists:
        user = user_doc.to_dict()
        new_count = max(0, user.get("post_count", 1) - 1)
        db.collection("users").document(session["user_id"]).update({
            "post_count": new_count
        })

    flash("Post deleted.", "success")
    return redirect(url_for("main.feed"))
