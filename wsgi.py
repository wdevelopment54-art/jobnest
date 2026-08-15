"""WSGI entry point for deployment (PythonAnywhere, etc.).

PythonAnywhere's web app config points at this module (or its contents are
pasted into the PA WSGI file). It must expose a WSGI callable named
``application``. The app uses a factory (``create_app``), so we build it here.

Key robustness measures for hosting platforms:
- Add the project directory to ``sys.path`` (computed from this file's
  location, so it works no matter where the project lives).
- Load ``.env`` if present (python-dotenv is optional on the server).
- Ensure the ``instance/`` folder exists so the SQLite DB can be created.
- Create database tables on startup if they do not exist yet, so the site
  loads instead of erroring with "no such table".
"""
import os
import sys

# Project home = the directory that contains this wsgi.py
PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))
if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Load environment variables from .env if it exists on the server.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_HOME, ".env"))
except Exception:
    # python-dotenv may not be installed on the server; that's fine because
    # config.py provides sensible defaults.
    pass

# Make sure the instance folder (where SQLite lives) exists and is writable.
os.makedirs(os.path.join(PROJECT_HOME, "instance"), exist_ok=True)

from app import create_app
from app.extensions import db

# Use the production config on the server (DEBUG off). Override with the
# FLASK_ENV environment variable if needed.
application = create_app(os.environ.get("FLASK_ENV", "production"))

# Create tables on first start so the site loads even if migrations were not
# run on the server. (Data still needs to be seeded / uploaded separately.)
with application.app_context():
    try:
        db.create_all()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[wsgi] db.create_all() failed: {exc}")
