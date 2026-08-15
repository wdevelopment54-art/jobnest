"""Notification service for creating in-app notifications."""
from app.extensions import db
from app.models import Notification


def notify(user_id, title, message, link=None):
    """Create and persist a notification for a user."""
    if not user_id:
        return None
    n = Notification(user_id=user_id, title=title, message=message, link=link)
    db.session.add(n)
    db.session.commit()
    return n


def notify_employer_new_application(employer_user_id, job_title, application_id):
    return notify(
        employer_user_id,
        "New Application Received",
        f"A new candidate applied for '{job_title}'.",
        link="/employer/applications",
    )


def notify_jobseeker_application_submitted(seeker_user_id, job_title):
    return notify(
        seeker_user_id,
        "Application Submitted",
        f"Your application for '{job_title}' was submitted successfully.",
        link="/seeker/applications",
    )


def notify_jobseeker_status_change(seeker_user_id, job_title, new_status):
    return notify(
        seeker_user_id,
        f"Application {new_status}",
        f"Your application for '{job_title}' is now: {new_status}.",
        link="/seeker/applications",
    )


def notify_employer_job_approved(employer_user_id, job_title):
    return notify(
        employer_user_id,
        "Job Approved",
        f"Your job posting '{job_title}' has been approved and is now public.",
        link="/employer/jobs",
    )


def notify_employer_job_rejected(employer_user_id, job_title):
    return notify(
        employer_user_id,
        "Job Rejected",
        f"Your job posting '{job_title}' was rejected by an administrator.",
        link="/employer/jobs",
    )


def notify_admin_new_employer(company_name):
    # Admin notifications go to all admin users
    from app.models import User
    admins = User.query.filter_by(role="admin").all()
    for a in admins:
        notify(a.id, "New Employer Registration",
               f"'{company_name}' registered and is awaiting approval.")


def notify_admin_new_job(job_title):
    from app.models import User
    admins = User.query.filter_by(role="admin").all()
    for a in admins:
        notify(a.id, "New Job Awaiting Approval",
               f"Job '{job_title}' was posted and needs approval.")


def notify_admin_new_message(name, subject):
    from app.models import User
    admins = User.query.filter_by(role="admin").all()
    for a in admins:
        notify(a.id, "New Contact Message",
               f"New message from {name} regarding: {subject}.")
