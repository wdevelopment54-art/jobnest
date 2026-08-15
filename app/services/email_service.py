"""Email service for password reset and notifications."""
import os
from datetime import datetime, timedelta

from flask import current_app, url_for
from flask_mail import Message

from app.extensions import mail, db
from app.models import User


def send_email(subject, recipients, html_body, text_body=None):
    try:
        msg = Message(subject, recipients=recipients)
        msg.html = html_body
        msg.body = text_body or html_body
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email send failed: {e}")
        return False


def generate_reset_token(user):
    """Create a signed token containing user id and expiry."""
    from itsdangerous import URLSafeTimedSerializer
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"user_id": user.id})


def verify_reset_token(token, max_age=3600):
    """Verify a reset token and return the user, or None if invalid/expired."""
    from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return db.session.get(User, data.get("user_id"))


def send_password_reset_email(user):
    token = generate_reset_token(user)
    reset_url = url_for("auth.reset_token", token=token, _external=True)
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;">
      <h2 style="color:#1e3a5f;">Job Portal Password Reset</h2>
      <p>Hello {user.full_name},</p>
      <p>We received a request to reset your password. Click the button below to choose a new password. This link expires in 1 hour.</p>
      <p><a href="{reset_url}" style="background:#1e3a5f;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none;">Reset Password</a></p>
      <p>If you did not request this, you can safely ignore this email.</p>
      <hr>
      <small>Job Portal Team</small>
    </div>
    """
    return send_email("Reset Your Password", [user.email], html)
