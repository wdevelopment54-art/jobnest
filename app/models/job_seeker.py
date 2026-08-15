"""Job seeker profile model."""
from datetime import datetime

from app.extensions import db


class JobSeeker(db.Model):
    __tablename__ = "job_seekers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    profile_picture = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    languages = db.Column(db.Text, nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = db.relationship("User", back_populates="job_seeker")
    applications = db.relationship(
        "Application", back_populates="job_seeker",
        cascade="all, delete-orphan"
    )
    saved_jobs = db.relationship(
        "SavedJob", back_populates="job_seeker",
        cascade="all, delete-orphan"
    )

    def profile_completion(self):
        """Return percentage of completed profile fields."""
        fields = [
            self.location, self.summary, self.education, self.skills,
            self.experience, self.resume, self.profile_picture,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    def __repr__(self):
        return f"<JobSeeker {self.id} user={self.user_id}>"
