from flask import Blueprint, request, session, jsonify
from firebase_config import get_db
from datetime import datetime, timezone
import uuid

api_bp = Blueprint("api", __name__)


@api_bp.route("/upvote/<post_id>", methods=["POST"])
def upvote(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    db = get_db()
    post_ref = db.collection("posts").document(post_id)
    post_doc = post_ref.get()

    if not post_doc.exists:
        return jsonify({"error": "Post not found"}), 404

    post = post_doc.to_dict()
    upvoted_by = post.get("upvoted_by", [])

    if session["user_id"] in upvoted_by:
        upvoted_by.remove(session["user_id"])
        post_ref.update({
            "upvotes": max(0, post.get("upvotes", 1) - 1),
            "upvoted_by": upvoted_by
        })
        return jsonify({"status": "removed", "count": max(0, post.get("upvotes", 1) - 1)})
    else:
        upvoted_by.append(session["user_id"])
        new_count = post.get("upvotes", 0) + 1
        post_ref.update({
            "upvotes": new_count,
            "upvoted_by": upvoted_by
        })

        author_id = post.get("author_id")
        if author_id:
            author_doc = db.collection("users").document(author_id).get()
            if author_doc.exists:
                author = author_doc.to_dict()
                db.collection("users").document(author_id).update({
                    "total_upvotes_received": author.get("total_upvotes_received", 0) + 1
                })

        return jsonify({"status": "added", "count": new_count})


@api_bp.route("/bookmark/<post_id>", methods=["POST"])
def bookmark(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    db = get_db()
    post_ref = db.collection("posts").document(post_id)
    post_doc = post_ref.get()

    if not post_doc.exists:
        return jsonify({"error": "Post not found"}), 404

    post = post_doc.to_dict()
    bookmarked_by = post.get("bookmarked_by", [])

    if session["user_id"] in bookmarked_by:
        bookmarked_by.remove(session["user_id"])
        post_ref.update({
            "bookmarks": max(0, post.get("bookmarks", 1) - 1),
            "bookmarked_by": bookmarked_by
        })
        return jsonify({"status": "removed"})
    else:
        bookmarked_by.append(session["user_id"])
        post_ref.update({
            "bookmarks": post.get("bookmarks", 0) + 1,
            "bookmarked_by": bookmarked_by
        })
        return jsonify({"status": "added"})


@api_bp.route("/comment/<post_id>", methods=["POST"])
def comment(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Comment cannot be empty"}), 400

    if len(content) > 2000:
        return jsonify({"error": "Comment too long"}), 400

    db = get_db()

    user_doc = db.collection("users").document(session["user_id"]).get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404

    user = user_doc.to_dict()
    now = datetime.now(timezone.utc).isoformat()
    comment_id = str(uuid.uuid4())

    comment_data = {
        "content": content,
        "author_id": session["user_id"],
        "author_name": user.get("name", ""),
        "author_handle": user.get("handle", ""),
        "author_avatar_letter": user.get("avatar_letter", "?"),
        "author_avatar_color": user.get("avatar_color", "#4111CC"),
        "created_at": now,
        "upvotes": 0
    }

    db.collection("posts").document(post_id) \
        .collection("comments").document(comment_id).set(comment_data)

    post_doc = db.collection("posts").document(post_id).get()
    if post_doc.exists:
        post = post_doc.to_dict()
        db.collection("posts").document(post_id).update({
            "comment_count": post.get("comment_count", 0) + 1
        })

    comment_data["id"] = comment_id
    return jsonify({"status": "success", "comment": comment_data})


@api_bp.route("/follow/<user_id>", methods=["POST"])
def follow(user_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    if session["user_id"] == user_id:
        return jsonify({"error": "Cannot follow yourself"}), 400

    db = get_db()
    target_ref = db.collection("users").document(user_id)
    target_doc = target_ref.get()

    if not target_doc.exists:
        return jsonify({"error": "User not found"}), 404

    target = target_doc.to_dict()
    followers = target.get("followers", [])

    current_ref = db.collection("users").document(session["user_id"])
    current_doc = current_ref.get()
    current = current_doc.to_dict()
    following = current.get("following", [])

    if session["user_id"] in followers:
        followers.remove(session["user_id"])
        following.remove(user_id) if user_id in following else None

        target_ref.update({
            "followers": followers,
            "followers_count": max(0, len(followers))
        })
        current_ref.update({
            "following": following,
            "following_count": max(0, len(following))
        })
        return jsonify({"status": "unfollowed", "count": len(followers)})
    else:
        followers.append(session["user_id"])
        following.append(user_id)

        target_ref.update({
            "followers": followers,
            "followers_count": len(followers)
        })
        current_ref.update({
            "following": following,
            "following_count": len(following)
        })
        return jsonify({"status": "followed", "count": len(followers)})


@api_bp.route("/human-check", methods=["POST"])
def human_check():
    data = request.get_json()
    text = data.get("text", "")

    from utils.humancheck import analyze_human_score
    result = analyze_human_score(text)

    return jsonify(result)
