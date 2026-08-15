"""Employer / company profile model."""
from datetime import datetime

from app.extensions import db

# Approval status constants
EMPLOYER_PENDING = "pending"
EMPLOYER_APPROVED = "approved"
EMPLOYER_REJECTED = "rejected"


class Employer(db.Model):
    __tablename__ = "employers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    company_name = db.Column(db.String(150), nullable=False)
    company_logo = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    company_size = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    approval_status = db.Column(
        db.String(20), default=EMPLOYER_PENDING, nullable=False, index=True
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    user = db.relationship("User", back_populates="employer")
    company = db.relationship("Company", back_populates="employer")
    jobs = db.relationship(
        "Job", back_populates="employer", cascade="all, delete-orphan"
    )

    @property
    def is_approved(self):
        return self.approval_status == EMPLOYER_APPROVED

    def __repr__(self):
        return f"<Employer {self.company_name}>"
