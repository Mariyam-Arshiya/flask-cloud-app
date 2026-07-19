from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, abort
from firebase_config import get_db
from utils.helpers import generate_slug, truncate_text, get_cover_image, extract_tags
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
        post_type = request.form.get("post_type", "regular")
        cover_url = request.form.get("cover_url", "").strip()
        what_failed = request.form.get("what_failed", "").strip()
        what_learned = request.form.get("what_learned", "").strip()
        github_repo = request.form.get("github_repo", "").strip()
        if not title or not content:
            flash("Title and content are required.", "error")
            return render_template("write.html")
        if len(content) < 30:
            flash("Write at least 30 characters.", "error")
            return render_template("write.html")
        if post_type == "dead_end" and not what_learned:
            flash("Dead-end posts need a 'what you learned' section. That's the whole point.", "error")
            return render_template("write.html")
        db = get_db()
        user_doc = db.collection("users").document(session["user_id"]).get()
        user = user_doc.to_dict()
        post_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        slug = generate_slug(title)
        if not cover_url:
            cover_url = get_cover_image(topic)
        tags = extract_tags(content + " " + title)
        post_data = {
            "title": title, "subtitle": subtitle, "content": content,
            "excerpt": truncate_text(content, 200), "slug": slug,
            "topic": topic, "post_type": post_type, "cover_url": cover_url,
            "tags": tags,
            "what_failed": what_failed, "what_learned": what_learned,
            "github_repo": github_repo,
            "author_id": session["user_id"],
            "author_name": user.get("name", ""),
            "author_handle": user.get("handle", ""),
            "author_avatar_letter": user.get("avatar_letter", "?"),
            "author_avatar_url": user.get("avatar_url", ""),
            "author_github_verified": user.get("github_verified", False),
            "created_at": now, "updated_at": now, "first_draft_at": now,
            "status": "published", "edit_count": 0, "current_version": 1,
            "likes": 0, "liked_by": [], "bookmarks": 0, "bookmarked_by": [],
            "comment_count": 0, "view_count": 0,
            "word_count": len(content.split()), "reports": 0, "hidden": False
        }
        db.collection("posts").document(post_id).set(post_data)
        db.collection("posts").document(post_id).collection("revisions").document("v1").set({
            "version": 1, "title": title, "content": content,
            "created_at": now, "note": "initial draft"
        })
        updates = {"post_count": user.get("post_count", 0) + 1}
        if post_type == "dead_end":
            updates["dead_end_count"] = user.get("dead_end_count", 0) + 1
        db.collection("users").document(session["user_id"]).update(updates)
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
    if post.get("hidden", False) and not session.get("is_admin", False):
        flash("This post is hidden.", "error")
        return redirect(url_for("main.feed"))
    post["id"] = post_id
    db.collection("posts").document(post_id).update({"view_count": post.get("view_count", 0) + 1})
    comments_ref = db.collection("posts").document(post_id).collection("comments").order_by("created_at", direction="ASCENDING")
    comments = []
    for doc in comments_ref.stream():
        c = doc.to_dict()
        c["id"] = doc.id
        comments.append(c)
    is_liked = False
    is_bookmarked = False
    if "user_id" in session:
        is_liked = session["user_id"] in post.get("liked_by", [])
        is_bookmarked = session["user_id"] in post.get("bookmarked_by", [])
    revisions_ref = db.collection("posts").document(post_id).collection("revisions").order_by("version", direction="ASCENDING")
    revisions = []
    for doc in revisions_ref.stream():
        r = doc.to_dict()
        r["id"] = doc.id
        revisions.append(r)
    more_ref = db.collection("posts").where("author_id", "==", post.get("author_id")).where("status", "==", "published").order_by("created_at", direction="DESCENDING").limit(4)
    more_posts = []
    for doc in more_ref.stream():
        if doc.id != post_id:
            mp = doc.to_dict()
            mp["id"] = doc.id
            more_posts.append(mp)
    return render_template("post_detail.html", post=post, comments=comments, is_liked=is_liked,
                           is_bookmarked=is_bookmarked, revisions=revisions, more_posts=more_posts[:3])


@post_bp.route("/<post_id>/edit", methods=["GET", "POST"])
def edit(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    post_doc = db.collection("posts").document(post_id).get()
    if not post_doc.exists:
        abort(404)
    post = post_doc.to_dict()
    if post.get("author_id") != session["user_id"]:
        flash("You can only edit your own posts.", "error")
        return redirect(url_for("post.view", post_id=post_id))
    post["id"] = post_id
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        subtitle = request.form.get("subtitle", "").strip()
        note = request.form.get("edit_note", "").strip() or "revision"
        if not title or not content:
            flash("Title and content are required.", "error")
            return render_template("edit.html", post=post)
        now = datetime.now(timezone.utc).isoformat()
        new_version = post.get("current_version", 1) + 1
        edit_count = post.get("edit_count", 0) + 1
        tags = extract_tags(content + " " + title)
        db.collection("posts").document(post_id).update({
            "title": title, "content": content, "subtitle": subtitle,
            "excerpt": truncate_text(content, 200), "tags": tags,
            "updated_at": now, "edit_count": edit_count, "current_version": new_version,
            "word_count": len(content.split())
        })
        db.collection("posts").document(post_id).collection("revisions").document(f"v{new_version}").set({
            "version": new_version, "title": title, "content": content,
            "created_at": now, "note": note
        })
        user_doc = db.collection("users").document(session["user_id"]).get()
        if user_doc.exists:
            user = user_doc.to_dict()
            db.collection("users").document(session["user_id"]).update({"total_edits": user.get("total_edits", 0) + 1})
        return redirect(url_for("post.view", post_id=post_id))
    return render_template("edit.html", post=post)


@post_bp.route("/<post_id>/revisions")
def revisions(post_id):
    db = get_db()
    post_doc = db.collection("posts").document(post_id).get()
    if not post_doc.exists:
        abort(404)
    post = post_doc.to_dict()
    post["id"] = post_id
    revs_ref = db.collection("posts").document(post_id).collection("revisions").order_by("version", direction="DESCENDING")
    revisions = []
    for doc in revs_ref.stream():
        r = doc.to_dict()
        r["id"] = doc.id
        revisions.append(r)
    return render_template("revisions.html", post=post, revisions=revisions)


@post_bp.route("/<post_id>/delete", methods=["POST"])
def delete(post_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    db = get_db()
    post_doc = db.collection("posts").document(post_id).get()
    if not post_doc.exists:
        abort(404)
    post = post_doc.to_dict()
    if post.get("author_id") != session["user_id"] and not session.get("is_admin", False):
        flash("Not authorized.", "error")
        return redirect(url_for("main.feed"))
    db.collection("posts").document(post_id).delete()
    user_doc = db.collection("users").document(session["user_id"]).get()
    if user_doc.exists:
        user = user_doc.to_dict()
        updates = {"post_count": max(0, user.get("post_count", 1) - 1)}
        if post.get("post_type") == "dead_end":
            updates["dead_end_count"] = max(0, user.get("dead_end_count", 1) - 1)
        db.collection("users").document(session["user_id"]).update(updates)
    return redirect(url_for("main.feed"))
