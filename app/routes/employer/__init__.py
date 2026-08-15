"""Employer portal blueprint."""
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort, current_app,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    Employer, Job, JobCategory, Application, SavedJob, Notification,
    JOB_PENDING, JOB_ACTIVE, JOB_INACTIVE, JOB_EXPIRED, JOB_REJECTED,
    APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW,
    APP_SELECTED, APP_REJECTED,
)
from app.forms import EmployerProfileForm, JobForm, ApplicationStatusForm
from app.utils import save_uploaded_file, delete_uploaded_file, upload_url
from app.services import notify_jobseeker_status_change
from app.utils.decorators import employer_required

bp = Blueprint("employer", __name__)


def get_employer_or_403():
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        abort(403)
    return employer


@bp.route("/dashboard")
@login_required
@employer_required
def dashboard():
    employer = get_employer_or_403()
    jobs = Job.query.filter_by(employer_id=employer.id).all()
    total_apps = 0
    new_apps = 0
    shortlisted = 0
    interviews = 0
    selected = 0
    for j in jobs:
        for a in j.applications:
            total_apps += 1
            if a.status == APP_APPLIED:
                new_apps += 1
            if a.status == APP_SHORTLISTED:
                shortlisted += 1
            if a.status == APP_INTERVIEW:
                interviews += 1
            if a.status == APP_SELECTED:
                selected += 1
    counts = {
        "total_jobs": len(jobs),
        "active_jobs": sum(1 for j in jobs if j.status == JOB_ACTIVE),
        "pending": sum(1 for j in jobs if j.status == JOB_PENDING),
        "expired": sum(1 for j in jobs if j.status == JOB_EXPIRED or j.is_expired),
        "total_apps": total_apps,
        "new_apps": new_apps,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "selected": selected,
    }
    recent_apps = []
    for j in jobs:
        recent_apps.extend(j.applications)
    recent_apps = sorted(recent_apps, key=lambda a: a.applied_at, reverse=True)[:6]
    recent_jobs = sorted(jobs, key=lambda j: j.created_at, reverse=True)[:5]
    notifications = current_user.notifications[:5]
    return render_template(
        "employer/dashboard.html", employer=employer, counts=counts,
        recent_apps=recent_apps, recent_jobs=recent_jobs,
        notifications=notifications, title="Employer Dashboard",
    )


@bp.route("/company-profile", methods=["GET", "POST"])
@login_required
@employer_required
def company_profile():
    employer = get_employer_or_403()
    form = EmployerProfileForm(obj=employer)
    if form.validate_on_submit():
        employer.company_name = form.company_name.data.strip()
        employer.industry = form.industry.data
        employer.company_size = form.company_size.data
        employer.location = form.location.data
        employer.website = form.website.data
        employer.contact_email = form.contact_email.data
        employer.phone = form.phone.data
        employer.description = form.description.data
        if form.company_logo.data:
            fname = save_uploaded_file(
                form.company_logo.data, "logos",
                current_app.config["ALLOWED_IMAGE_EXTENSIONS"])
            if fname:
                delete_uploaded_file(employer.company_logo)
                employer.company_logo = fname
        db.session.commit()
        flash("Company profile updated.", "success")
        return redirect(url_for("employer.company_profile"))
    return render_template(
        "employer/company_profile.html", form=form, employer=employer,
        logo_url=upload_url(employer.company_logo), title="Company Profile",
    )


@bp.route("/jobs")
@login_required
@employer_required
def jobs():
    employer = get_employer_or_403()
    status = request.args.get("status", "").strip()
    query = Job.query.filter_by(employer_id=employer.id)
    if status:
        query = query.filter_by(status=status)
    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template(
        "employer/jobs.html", jobs=jobs, current_status=status,
        statuses=[JOB_PENDING, JOB_ACTIVE, JOB_INACTIVE, JOB_REJECTED, JOB_EXPIRED],
        title="My Jobs",
    )


@bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@employer_required
def new_job():
    employer = get_employer_or_403()
    if employer.approval_status != "approved":
        flash("Your employer account must be approved before posting jobs.", "warning")
        return redirect(url_for("employer.company_profile"))
    form = JobForm()
    form.category_id.choices = [(c.id, c.name) for c in
                                JobCategory.query.filter_by(is_active=True)]
    if form.validate_on_submit():
        from config import Config
        auto = Config.AUTO_PUBLISH_JOBS
        status = JOB_ACTIVE if auto else JOB_PENDING
        job = Job(
            employer_id=employer.id,
            category_id=form.category_id.data or None,
            title=form.title.data.strip(),
            description=form.description.data,
            responsibilities=form.responsibilities.data,
            requirements=form.requirements.data,
            skills=form.skills.data,
            education=form.education.data,
            experience=form.experience.data,
            salary=form.salary.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            company_id=employer.company_id,
            location=form.location.data.strip(),
            employment_type=form.employment_type.data,
            deadline=form.deadline.data,
            benefits=form.benefits.data,
            status=status,
        )
        db.session.add(job)
        db.session.commit()
        if auto:
            flash("Job posted and published successfully.", "success")
        else:
            flash("Job submitted. It is pending admin approval.", "info")
        return redirect(url_for("employer.jobs"))
    return render_template("employer/job_form.html", form=form,
                           title="Post a Job")


@bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@employer_required
def edit_job(job_id):
    employer = get_employer_or_403()
    job = Job.query.get_or_404(job_id)
    if job.employer_id != employer.id:
        abort(403)
    form = JobForm(obj=job)
    form.category_id.choices = [(c.id, c.name) for c in
                                JobCategory.query.filter_by(is_active=True)]
    if form.validate_on_submit():
        job.category_id = form.category_id.data or None
        job.title = form.title.data.strip()
        job.description = form.description.data
        job.responsibilities = form.responsibilities.data
        job.requirements = form.requirements.data
        job.skills = form.skills.data
        job.education = form.education.data
        job.experience = form.experience.data
        job.salary = form.salary.data
        job.salary_min = form.salary_min.data
        job.salary_max = form.salary_max.data
        job.location = form.location.data.strip()
        job.employment_type = form.employment_type.data
        job.deadline = form.deadline.data
        job.benefits = form.benefits.data
        db.session.commit()
        flash("Job updated successfully.", "success")
        return redirect(url_for("employer.jobs"))
    return render_template("employer/job_form.html", form=form, job=job,
                           title="Edit Job")


@bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@employer_required
def delete_job(job_id):
    employer = get_employer_or_403()
    job = Job.query.get_or_404(job_id)
    if job.employer_id != employer.id:
        abort(403)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "info")
    return redirect(url_for("employer.jobs"))


@bp.route("/jobs/<int:job_id>/toggle", methods=["POST"])
@login_required
@employer_required
def toggle_job(job_id):
    employer = get_employer_or_403()
    job = Job.query.get_or_404(job_id)
    if job.employer_id != employer.id:
        abort(403)
    if job.status == JOB_ACTIVE:
        job.status = JOB_INACTIVE
        flash("Job deactivated.", "info")
    elif job.status == JOB_INACTIVE:
        job.status = JOB_ACTIVE
        flash("Job activated.", "success")
    else:
        flash("Only active/inactive jobs can be toggled.", "warning")
    db.session.commit()
    return redirect(url_for("employer.jobs"))


@bp.route("/applications")
@login_required
@employer_required
def applications():
    employer = get_employer_or_403()
    job_id = request.args.get("job_id", type=int)
    status = request.args.get("status", "").strip()
    job_ids = [j.id for j in Job.query.filter_by(employer_id=employer.id).all()]
    query = Application.query.filter(Application.job_id.in_(job_ids))
    if job_id:
        query = query.filter_by(job_id=job_id)
    if status:
        query = query.filter_by(status=status)
    apps = query.order_by(Application.applied_at.desc()).all()
    jobs = Job.query.filter_by(employer_id=employer.id).all()
    return render_template(
        "employer/applications.html", applications=apps, jobs=jobs,
        current_job=job_id, current_status=status,
        statuses=[APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW,
                  APP_SELECTED, APP_REJECTED],
        title="Applications",
    )


@bp.route("/applications/<int:app_id>", methods=["GET", "POST"])
@login_required
@employer_required
def application_detail(app_id):
    employer = get_employer_or_403()
    app = Application.query.get_or_404(app_id)
    if app.job.employer_id != employer.id:
        abort(403)
    form = ApplicationStatusForm(obj=app)
    form.status.choices = [(s, s) for s in
                           [APP_APPLIED, APP_REVIEW, APP_SHORTLISTED,
                            APP_INTERVIEW, APP_SELECTED, APP_REJECTED]]
    if form.validate_on_submit():
        old_status = app.status
        app.status = form.status.data
        app.interview_date = form.interview_date.data
        app.interview_time = form.interview_time.data
        app.interview_notes = form.interview_notes.data
        app.employer_notes = form.employer_notes.data
        app.rejection_reason = form.rejection_reason.data if form.status.data == APP_REJECTED else None
        app.status_updated_at = db.func.now()
        db.session.commit()
        if old_status != app.status:
            notify_jobseeker_status_change(
                app.job_seeker.user_id, app.job.title, app.status)
            flash("Application status updated and candidate notified.", "success")
        else:
            flash("Application notes updated.", "success")
        return redirect(url_for("employer.application_detail", app_id=app.id))
    resume_url = upload_url(app.resume)
    return render_template(
        "employer/application_detail.html", application=app, form=form,
        resume_url=resume_url, title="Application Detail",
    )


@bp.route("/notifications")
@login_required
@employer_required
def notifications():
    notes = current_user.notifications
    return render_template("employer/notifications.html",
                           notifications=notes, title="Notifications")
