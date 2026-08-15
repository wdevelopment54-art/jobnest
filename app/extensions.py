"""Shared Flask extensions (initialized without an app instance)."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Configure login manager defaults
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
login_manager.login_message = "Please log in to access this page."
