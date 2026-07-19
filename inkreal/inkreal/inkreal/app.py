from flask import Flask, render_template
from config import Config
from firebase_config import init_firebase, is_ready


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_firebase()

    from routes.main import main_bp
    from routes.auth_routes import auth_bp
    from routes.post_routes import post_bp
    from routes.profile_routes import profile_bp
    from routes.community_routes import community_bp
    from routes.api_routes import api_bp
    from routes.github_routes import github_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/post")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(community_bp, url_prefix="/community")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(github_bp, url_prefix="/gh")

    @app.template_filter("timeago")
    def timeago_filter(t):
        from utils.helpers import time_ago
        return time_ago(t)

    @app.template_filter("readtime")
    def readtime_filter(t):
        from utils.helpers import reading_time
        return reading_time(t)

    @app.template_filter("markdown")
    def markdown_filter(t):
        from utils.helpers import render_markdown
        return render_markdown(t)

    @app.template_filter("duration")
    def duration_filter(t):
        from utils.helpers import duration_since
        return duration_since(t)

    @app.context_processor
    def inject_globals():
        return {"firebase_ready": is_ready()}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="This page does not exist."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Something broke on our end."), 500

    @app.errorhandler(RuntimeError)
    def runtime_error(e):
        return render_template("error.html", code=500, message=str(e)), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
