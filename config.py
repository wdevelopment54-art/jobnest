import os
from datetime import timedelta


class Config:
    """Base configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/job_portal",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Uploads
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", "5")) * 1024 * 1024
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "noreply@jobportal.com"
    )

    # Misc
    PER_PAGE = int(os.environ.get("PER_PAGE", "9"))
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Whether new employer jobs are auto-published (otherwise pending approval)
    AUTO_PUBLISH_JOBS = os.environ.get("AUTO_PUBLISH_JOBS", "False").lower() == "true"

    # ---- Site / business contact info (configurable via env) ----
    SITE_NAME = os.environ.get("SITE_NAME", "JOBNEST")
    SITE_EMAIL = os.environ.get("SITE_EMAIL", "info@yourjobportal.com")
    SITE_PHONE_DISPLAY = os.environ.get("SITE_PHONE_DISPLAY", "0309-6890020")
    SITE_PHONE_HREF = os.environ.get("SITE_PHONE_HREF", "tel:03096890020")
    SITE_WHATSAPP_NUMBER = os.environ.get("SITE_WHATSAPP_NUMBER", "0309-6890020")
    SITE_WHATSAPP_HREF = os.environ.get("SITE_WHATSAPP_HREF", "https://wa.me/923096890020")
    SITE_WHATSAPP_MESSAGE = os.environ.get(
        "SITE_WHATSAPP_MESSAGE",
        "Hello, I would like to know more about your Job Portal services.",
    )
    SITE_CITY = os.environ.get("SITE_CITY", "Kot Radha Kishen")
    SITE_STATE = os.environ.get("SITE_STATE", "Punjab")
    SITE_COUNTRY = os.environ.get("SITE_COUNTRY", "Pakistan")
    SITE_ADDRESS = os.environ.get("SITE_ADDRESS", "Kot Radha Kishen, Punjab, Pakistan")
    SITE_MAP_URL = os.environ.get(
        "SITE_MAP_URL",
        "https://www.google.com/maps/search/?api=1&query=Kot+Radha+Kishen+Punjab+Pakistan",
    )
    SITE_FACEBOOK_URL = os.environ.get("SITE_FACEBOOK_URL", "#")
    SITE_TWITTER_URL = os.environ.get("SITE_TWITTER_URL", "#")
    SITE_LINKEDIN_URL = os.environ.get("SITE_LINKEDIN_URL", "#")
    SITE_INSTAGRAM_URL = os.environ.get("SITE_INSTAGRAM_URL", "#")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
