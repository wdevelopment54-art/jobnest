"""Application factory for the Job Portal."""
import os
from flask import Flask, render_template
from flask_login import current_user

from app.extensions import db, migrate, login_manager, mail, csrf
from config import config_by_name
from app.utils.helpers import time_ago, format_date, status_badge_class


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure upload folder exists
    upload_folder = os.path.join(
        app.root_path, "static", "uploads"
    )
    os.makedirs(upload_folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Register Jinja globals
    app.jinja_env.globals["time_ago"] = time_ago
    app.jinja_env.globals["format_date"] = format_date
    app.jinja_env.globals["status_badge_class"] = status_badge_class
    app.jinja_env.globals["current_user"] = current_user

    # Register custom filters
    @app.template_filter("nl2br")
    def nl2br_filter(value):
        if not value:
            return ""
        return value.replace("\r\n", "\n").replace("\n", "<br>\n")

    # Register blueprints
    from app.routes.public import bp as public_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.seeker import bp as seeker_bp
    from app.routes.employer import bp as employer_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(seeker_bp, url_prefix="/seeker")
    app.register_blueprint(employer_bp, url_prefix="/employer")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models.job import JobCategory
        categories = []
        try:
            categories = (
                JobCategory.query.filter_by(is_active=True)
                .order_by(JobCategory.name)
                .all()
            )
        except Exception:
            categories = []
        # Start from config defaults, then override with any admin-edited
        # site settings stored in the database (so the admin panel controls
        # the whole site's branding/contact/social without code changes).
        site = {k: app.config.get(k) for k in [
            "SITE_NAME", "SITE_EMAIL", "SITE_PHONE_DISPLAY", "SITE_PHONE_HREF",
            "SITE_WHATSAPP_NUMBER", "SITE_WHATSAPP_HREF", "SITE_WHATSAPP_MESSAGE",
            "SITE_CITY", "SITE_STATE", "SITE_COUNTRY", "SITE_ADDRESS",
            "SITE_MAP_URL", "SITE_FACEBOOK_URL", "SITE_TWITTER_URL",
            "SITE_LINKEDIN_URL", "SITE_INSTAGRAM_URL",
        ]}
        try:
            from app.models import SiteSetting
            for k, v in SiteSetting.get_all().items():
                if v not in (None, ""):
                    site[k] = v
        except Exception:
            # Database may not be available (e.g. before first migration);
            # fall back to config values above.
            pass
        return {
            "current_year": os.environ.get("CURRENT_YEAR", "2026"),
            "nav_categories": categories[:8],
            "site": site,
        }

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/error.html", code=400,
                               title="Bad Request",
                               message="The server could not understand the request."), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/error.html", code=403,
                               title="Forbidden",
                               message="You do not have permission to access this page."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/error.html", code=404,
                               title="Page Not Found",
                               message="The page you are looking for does not exist."), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/error.html", code=500,
                               title="Internal Server Error",
                               message="Something went wrong on our end. Please try again later."), 500

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return db.session.get(User, int(user_id))
