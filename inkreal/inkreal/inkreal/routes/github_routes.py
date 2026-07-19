from flask import Blueprint, request, session, redirect, url_for, flash
from firebase_config import get_db
from config import Config
import requests
import uuid

github_bp = Blueprint("github", __name__)


@github_bp.route("/connect")
def connect():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if not Config.GITHUB_CLIENT_ID:
        flash("GitHub OAuth not configured. Add GITHUB_CLIENT_ID to .env", "error")
        return redirect(url_for("profile.settings"))
    state = uuid.uuid4().hex
    session["gh_state"] = state
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={Config.GITHUB_CLIENT_ID}"
        f"&redirect_uri={Config.APP_BASE_URL}/gh/callback"
        f"&scope=read:user"
        f"&state={state}"
    )
    return redirect(url)


@github_bp.route("/callback")
def callback():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    code = request.args.get("code")
    state = request.args.get("state")
    if not code or state != session.get("gh_state"):
        flash("Invalid GitHub response.", "error")
        return redirect(url_for("profile.settings"))
    try:
        token_res = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": Config.GITHUB_CLIENT_ID, "client_secret": Config.GITHUB_CLIENT_SECRET, "code": code},
            timeout=10
        )
        token = token_res.json().get("access_token")
        if not token:
            flash("Could not get GitHub token.", "error")
            return redirect(url_for("profile.settings"))
        user_res = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"}, timeout=10)
        gh = user_res.json()
        username = gh.get("login", "")
        if not username:
            flash("Could not get GitHub username.", "error")
            return redirect(url_for("profile.settings"))
        db = get_db()
        db.collection("users").document(session["user_id"]).update({
            "github_username": username, "github_verified": True,
            "github_url": gh.get("html_url", ""), "github_avatar": gh.get("avatar_url", "")
        })
        flash(f"Connected to GitHub as {username}.", "success")
    except Exception as e:
        flash(f"GitHub connection failed: {str(e)[:100]}", "error")
    return redirect(url_for("profile.settings"))
