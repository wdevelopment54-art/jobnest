"""Job category and Job models."""
from datetime import datetime

from app.extensions import db

# Job status constants
JOB_PENDING = "pending"
JOB_APPROVED = "approved"
JOB_REJECTED = "rejected"
JOB_ACTIVE = "active"
JOB_INACTIVE = "inactive"
JOB_EXPIRED = "expired"
# Spec-aligned statuses
JOB_DRAFT = "draft"
JOB_CLOSED = "closed"

# Employment types (spec-aligned, lowercase keys)
EMPLOYMENT_TYPES = [
    "full_time", "part_time", "internship", "contract", "remote",
]
EMPLOYMENT_TYPE_LABELS = {
    "full_time": "Full Time",
    "part_time": "Part Time",
    "internship": "Internship",
    "contract": "Contract",
    "remote": "Remote",
}

# Experience levels
EXPERIENCE_LEVELS = [
    "Entry Level", "1-2 Years", "3-5 Years", "5-8 Years", "8+ Years",
]


class JobCategory(db.Model):
    __tablename__ = "job_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    jobs = db.relationship("Job", back_populates="category")

    def __repr__(self):
        return f"<JobCategory {self.name}>"


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(
        db.Integer, db.ForeignKey("employers.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("job_categories.id"), nullable=True, index=True
    )
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    education = db.Column(db.String(200), nullable=True)
    experience = db.Column(db.String(50), nullable=True)
    salary = db.Column(db.String(100), nullable=True)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    currency = db.Column(db.String(10), nullable=True, default="PKR")
    location = db.Column(db.String(120), nullable=False, index=True)
    employment_type = db.Column(db.String(30), nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=JOB_PENDING, nullable=False, index=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    employer = db.relationship("Employer", back_populates="jobs")
    company = db.relationship("Company", back_populates="jobs")
    category = db.relationship("JobCategory", back_populates="jobs")
    applications = db.relationship(
        "Application", back_populates="job", cascade="all, delete-orphan"
    )
    saved_by = db.relationship(
        "SavedJob", back_populates="job", cascade="all, delete-orphan"
    )

    @property
    def is_public(self):
        """A job is publicly visible only when active and not expired."""
        if self.status != JOB_ACTIVE:
            return False
        if self.deadline and self.deadline < datetime.utcnow().date():
            return False
        return True

    @property
    def is_expired(self):
        return self.deadline and self.deadline < datetime.utcnow().date()

    @property
    def employment_type_label(self):
        return EMPLOYMENT_TYPE_LABELS.get(self.employment_type, self.employment_type)

    def __repr__(self):
        return f"<Job {self.title}>"
