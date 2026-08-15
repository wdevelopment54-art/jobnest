"""Application, SavedJob and Notification models."""
from datetime import datetime

from app.extensions import db

# Application status constants
APP_APPLIED = "Applied"
APP_REVIEW = "Under Review"
APP_SHORTLISTED = "Shortlisted"
APP_INTERVIEW = "Interview"
APP_SELECTED = "Selected"
APP_REJECTED = "Rejected"

APPLICATION_STATUSES = [
    APP_APPLIED, APP_REVIEW, APP_SHORTLISTED,
    APP_INTERVIEW, APP_SELECTED, APP_REJECTED,
]


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("job_id", "job_seeker_id", name="uq_job_seeker_application"),
    )

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(
        db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    applicant_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    job_seeker_id = db.Column(
        db.Integer, db.ForeignKey("job_seekers.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    resume = db.Column(db.String(255), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=APP_APPLIED, nullable=False, index=True)
    interview_date = db.Column(db.Date, nullable=True)
    interview_time = db.Column(db.String(20), nullable=True)
    interview_notes = db.Column(db.Text, nullable=True)
    employer_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    status_updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    job = db.relationship("Job", back_populates="applications")
    job_seeker = db.relationship("JobSeeker", back_populates="applications")

    def __repr__(self):
        return f"<Application {self.id} job={self.job_id} seeker={self.job_seeker_id}>"


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"
    __table_args__ = (
        db.UniqueConstraint("job_seeker_id", "job_id", name="uq_saved_job"),
    )

    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(
        db.Integer, db.ForeignKey("job_seekers.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    job_id = db.Column(
        db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    job_seeker = db.relationship("JobSeeker", back_populates="saved_jobs")
    job = db.relationship("Job", back_populates="saved_by")

    def __repr__(self):
        return f"<SavedJob seeker={self.job_seeker_id} job={self.job_id}>"


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.title}>"
