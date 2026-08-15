"""User account model and role constants."""
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager
from flask_login import UserMixin


ROLE_ADMIN = "admin"
ROLE_EMPLOYER = "employer"
ROLE_JOBSEEKER = "jobseeker"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_JOBSEEKER)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    job_seeker = db.relationship(
        "JobSeeker", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    employer = db.relationship(
        "Employer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan",
        order_by="Notification.created_at.desc()",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_employer(self):
        return self.role == ROLE_EMPLOYER

    @property
    def is_jobseeker(self):
        return self.role == ROLE_JOBSEEKER

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
