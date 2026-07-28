from flask import Flask
from config import Config
from firebase_config import init_firebase


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

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(post_bp, url_prefix="/post")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(community_bp, url_prefix="/community")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.template_filter("timeago")
    def timeago_filter(timestamp):
        from utils.helpers import time_ago
        return time_ago(timestamp)

    @app.template_filter("readtime")
    def readtime_filter(content):
        from utils.helpers import reading_time
        return reading_time(content)

    @app.template_filter("markdown")
    def markdown_filter(text):
        from utils.helpers import render_markdown
        return render_markdown(text)

    @app.errorhandler(404)
    def not_found(e):
        return """<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:'Charter','Georgia',serif;background:#FAF8F5;color:#1a1a1a;"><div style="text-align:center;"><h1 style="font-size:72px;font-weight:300;margin:0;color:#4111CC;">404</h1><p style="font-size:20px;color:#666;margin-top:12px;">This page does not exist.</p><a href="/" style="display:inline-block;margin-top:24px;padding:12px 32px;background:#4111CC;color:#fff;text-decoration:none;border-radius:6px;font-size:15px;">Go Home</a></div></div>""", 404

    @app.errorhandler(500)
    def server_error(e):
        return """<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:'Charter','Georgia',serif;background:#FAF8F5;color:#1a1a1a;"><div style="text-align:center;"><h1 style="font-size:72px;font-weight:300;margin:0;color:#4111CC;">500</h1><p style="font-size:20px;color:#666;margin-top:12px;">Something went wrong.</p><a href="/" style="display:inline-block;margin-top:24px;padding:12px 32px;background:#4111CC;color:#fff;text-decoration:none;border-radius:6px;font-size:15px;">Go Home</a></div></div>""", 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
