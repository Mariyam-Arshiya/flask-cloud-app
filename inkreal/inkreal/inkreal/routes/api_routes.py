from flask import Blueprint, request, session, jsonify
from firebase_config import get_db
from datetime import datetime, timezone
import uuid

api_bp = Blueprint("api", __name__)


@api_bp.route("/like/<post_id>", methods=["POST"])
def like(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    ref = db.collection("posts").document(post_id)
    doc = ref.get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404
    post = doc.to_dict()
    liked = post.get("liked_by", [])
    if session["user_id"] in liked:
        liked.remove(session["user_id"])
        count = max(0, post.get("likes", 1) - 1)
        ref.update({"likes": count, "liked_by": liked})
        return jsonify({"status": "removed", "count": count})
    liked.append(session["user_id"])
    count = post.get("likes", 0) + 1
    ref.update({"likes": count, "liked_by": liked})
    return jsonify({"status": "added", "count": count})


@api_bp.route("/bookmark/<post_id>", methods=["POST"])
def bookmark(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    ref = db.collection("posts").document(post_id)
    doc = ref.get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404
    post = doc.to_dict()
    bm = post.get("bookmarked_by", [])
    if session["user_id"] in bm:
        bm.remove(session["user_id"])
        ref.update({"bookmarks": max(0, post.get("bookmarks", 1) - 1), "bookmarked_by": bm})
        return jsonify({"status": "removed"})
    bm.append(session["user_id"])
    ref.update({"bookmarks": post.get("bookmarks", 0) + 1, "bookmarked_by": bm})
    return jsonify({"status": "added"})


@api_bp.route("/comment/<post_id>", methods=["POST"])
def comment(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    data = request.get_json()
    content = (data.get("content") or "").strip()
    if not content or len(content) > 2000:
        return jsonify({"error": "Invalid comment"}), 400
    db = get_db()
    u = db.collection("users").document(session["user_id"]).get()
    if not u.exists:
        return jsonify({"error": "User not found"}), 404
    user = u.to_dict()
    now = datetime.now(timezone.utc).isoformat()
    cid = str(uuid.uuid4())
    cd = {
        "content": content, "author_id": session["user_id"],
        "author_name": user.get("name", ""), "author_handle": user.get("handle", ""),
        "author_avatar_letter": user.get("avatar_letter", "?"),
        "author_avatar_url": user.get("avatar_url", ""),
        "created_at": now, "likes": 0
    }
    db.collection("posts").document(post_id).collection("comments").document(cid).set(cd)
    pd = db.collection("posts").document(post_id).get()
    if pd.exists:
        db.collection("posts").document(post_id).update({"comment_count": pd.to_dict().get("comment_count", 0) + 1})
    cd["id"] = cid
    return jsonify({"status": "success", "comment": cd})


@api_bp.route("/follow/<user_id>", methods=["POST"])
def follow(user_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    if session["user_id"] == user_id:
        return jsonify({"error": "Cannot follow yourself"}), 400
    db = get_db()
    tref = db.collection("users").document(user_id)
    td = tref.get()
    if not td.exists:
        return jsonify({"error": "Not found"}), 404
    target = td.to_dict()
    followers = target.get("followers", [])
    cref = db.collection("users").document(session["user_id"])
    current = cref.get().to_dict()
    following = current.get("following", [])
    if session["user_id"] in followers:
        followers.remove(session["user_id"])
        if user_id in following:
            following.remove(user_id)
        tref.update({"followers": followers, "followers_count": len(followers)})
        cref.update({"following": following, "following_count": len(following)})
        return jsonify({"status": "unfollowed", "count": len(followers)})
    followers.append(session["user_id"])
    following.append(user_id)
    tref.update({"followers": followers, "followers_count": len(followers)})
    cref.update({"following": following, "following_count": len(following)})
    return jsonify({"status": "followed", "count": len(followers)})


@api_bp.route("/report/<post_id>", methods=["POST"])
def report(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    data = request.get_json() or {}
    reason = (data.get("reason") or "unspecified").strip()[:200]
    db = get_db()
    ref = db.collection("posts").document(post_id)
    doc = ref.get()
    if not doc.exists:
        return jsonify({"error": "Not found"}), 404
    post = doc.to_dict()
    ref.update({"reports": post.get("reports", 0) + 1})
    db.collection("reports").document(str(uuid.uuid4())).set({
        "post_id": post_id, "reported_by": session["user_id"],
        "reason": reason, "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved": False
    })
    return jsonify({"status": "reported"})


@api_bp.route("/onboarded", methods=["POST"])
def onboarded():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    db = get_db()
    db.collection("users").document(session["user_id"]).update({"onboarded": True})
    return jsonify({"status": "ok"})
