"""Company profile model (spec: companies table)."""
from datetime import datetime

from app.extensions import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    company_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    logo = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = db.relationship("User", backref="companies")
    jobs = db.relationship(
        "Job", back_populates="company", cascade="all, delete-orphan"
    )
    employer = db.relationship(
        "Employer", back_populates="company", uselist=False
    )

    def __repr__(self):
        return f"<Company {self.company_name}>"
