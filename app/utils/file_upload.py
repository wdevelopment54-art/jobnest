"""Secure file upload helpers."""
import os
import secrets
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_set):
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed_set


def save_uploaded_file(file, subfolder, allowed_extensions):
    """Save an uploaded file with a secure random name. Returns the stored filename."""
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename, allowed_extensions):
        return None

    ext = file.filename.rsplit(".", 1)[-1].lower()
    random_hex = secrets.token_hex(16)
    unique_name = f"{uuid.uuid4().hex}_{random_hex}.{ext}"
    # Use a subfolder to keep uploads organized and outside executable paths
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, unique_name)
    file.save(path)
    # Return a path relative to UPLOAD_FOLDER for storage in DB
    return os.path.join(subfolder, unique_name).replace("\\", "/")


def delete_uploaded_file(relative_path):
    """Delete a previously stored upload if it exists."""
    if not relative_path:
        return
    base = current_app.config["UPLOAD_FOLDER"]
    full = os.path.join(base, relative_path)
    try:
        if os.path.isfile(full):
            os.remove(full)
    except Exception:
        pass


def upload_url(relative_path):
    """Build a static URL for an uploaded file."""
    if not relative_path:
        return None
    return f"/static/uploads/{relative_path}"
