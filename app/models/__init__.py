"""Models package."""
from app.models.user import User, ROLE_ADMIN, ROLE_EMPLOYER, ROLE_JOBSEEKER
from app.models.job_seeker import JobSeeker
from app.models.employer import (
    Employer, EMPLOYER_PENDING, EMPLOYER_APPROVED, EMPLOYER_REJECTED,
)
from app.models.company import Company

from app.models.job import (
    Job, JobCategory, JOB_PENDING, JOB_APPROVED, JOB_REJECTED,
    JOB_ACTIVE, JOB_INACTIVE, JOB_EXPIRED, JOB_DRAFT, JOB_CLOSED, EMPLOYMENT_TYPES, EMPLOYMENT_TYPE_LABELS, EXPERIENCE_LEVELS,
)
from app.models.application import (
    Application, SavedJob, Notification,
    APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW,
    APP_SELECTED, APP_REJECTED, APPLICATION_STATUSES,
)
from app.models.contact import ContactMessage
from app.models.site_setting import SiteSetting

__all__ = [
    "User", "ROLE_ADMIN", "ROLE_EMPLOYER", "ROLE_JOBSEEKER",
    "JobSeeker",
    "Employer", "EMPLOYER_PENDING", "EMPLOYER_APPROVED", "EMPLOYER_REJECTED",
    "Company",
    "Job", "JobCategory", "JOB_PENDING", "JOB_APPROVED", "JOB_REJECTED",
    "JOB_ACTIVE", "JOB_INACTIVE", "JOB_EXPIRED", "EMPLOYMENT_TYPES", "EXPERIENCE_LEVELS",
    "Application", "SavedJob", "Notification",
    "APP_APPLIED", "APP_REVIEW", "APP_SHORTLISTED", "APP_INTERVIEW",
    "APP_SELECTED", "APP_REJECTED", "APPLICATION_STATUSES",
    "ContactMessage", "SiteSetting",
]
