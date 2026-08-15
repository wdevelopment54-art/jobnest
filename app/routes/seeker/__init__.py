"""Job Seeker portal blueprint."""
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort, current_app,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    Job, JobSeeker, Application, SavedJob, Notification,
    JOB_ACTIVE, APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW,
    APP_SELECTED, APP_REJECTED,
)
from app.forms import JobSeekerProfileForm, ApplicationForm
from app.utils import save_uploaded_file, delete_uploaded_file, upload_url
from app.services import (
    notify_employer_new_application, notify_jobseeker_application_submitted,
)
from app.utils.decorators import jobseeker_required

bp = Blueprint("seeker", __name__)


@bp.route("/dashboard")
@login_required
@jobseeker_required
def dashboard():
    seeker = current_user.job_seeker
    applications = seeker.applications
    counts = {
        "total": len(applications),
        "pending": sum(1 for a in applications if a.status == APP_APPLIED),
        "review": sum(1 for a in applications if a.status == APP_REVIEW),
        "shortlisted": sum(1 for a in applications if a.status == APP_SHORTLISTED),
        "interview": sum(1 for a in applications if a.status == APP_INTERVIEW),
        "selected": sum(1 for a in applications if a.status == APP_SELECTED),
        "rejected": sum(1 for a in applications if a.status == APP_REJECTED),
        "saved": len(seeker.saved_jobs),
    }
    recent_apps = sorted(applications, key=lambda a: a.applied_at, reverse=True)[:5]
    notifications = current_user.notifications[:5]
    # Recommended jobs (public, not already applied)
    applied_job_ids = {a.job_id for a in applications}
    recommended = (
        Job.query.filter(Job.status == JOB_ACTIVE)
        .order_by(Job.created_at.desc()).limit(4).all()
    )
    recommended = [j for j in recommended if j.id not in applied_job_ids][:4]
    return render_template(
        "seeker/dashboard.html", seeker=seeker, counts=counts,
        recent_apps=recent_apps, notifications=notifications,
        recommended=recommended, completion=seeker.profile_completion(),
        title="Job Seeker Dashboard",
    )


@bp.route("/profile", methods=["GET", "POST"])
@login_required
@jobseeker_required
def profile():
    seeker = current_user.job_seeker
    form = JobSeekerProfileForm(obj=seeker)
    # populate email/name from user
    if request.method == "GET":
        form.email.data = current_user.email
        form.full_name.data = current_user.full_name
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.phone = form.phone.data
        seeker.location = form.location.data
        seeker.summary = form.summary.data
        seeker.education = form.education.data
        seeker.skills = form.skills.data
        seeker.experience = form.experience.data
        seeker.certifications = form.certifications.data
        seeker.languages = form.languages.data

        if form.profile_picture.data:
            fname = save_uploaded_file(
                form.profile_picture.data, "profiles",
                current_app.config["ALLOWED_IMAGE_EXTENSIONS"])
            if fname:
                delete_uploaded_file(seeker.profile_picture)
                seeker.profile_picture = fname
        if form.resume.data:
            rname = save_uploaded_file(
                form.resume.data, "resumes",
                current_app.config["ALLOWED_RESUME_EXTENSIONS"])
            if rname:
                delete_uploaded_file(seeker.resume)
                seeker.resume = rname
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("seeker.profile"))
    return render_template(
        "seeker/profile.html", form=form, seeker=seeker,
        resume_url=upload_url(seeker.resume),
        picture_url=upload_url(seeker.profile_picture),
        title="My Profile",
    )


@bp.route("/profile/delete-resume", methods=["POST"])
@login_required
@jobseeker_required
def delete_resume():
    seeker = current_user.job_seeker
    delete_uploaded_file(seeker.resume)
    seeker.resume = None
    db.session.commit()
    flash("Resume deleted.", "info")
    return redirect(url_for("seeker.profile"))


@bp.route("/applications")
@login_required
@jobseeker_required
def applications():
    seeker = current_user.job_seeker
    status_filter = request.args.get("status", "").strip()
    query = Application.query.filter_by(job_seeker_id=seeker.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    apps = query.order_by(Application.applied_at.desc()).all()
    return render_template(
        "seeker/applications.html", applications=apps,
        statuses=[APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW,
                  APP_SELECTED, APP_REJECTED],
        current_status=status_filter, title="My Applications",
    )


@bp.route("/saved")
@login_required
@jobseeker_required
def saved_jobs():
    seeker = current_user.job_seeker
    saved = SavedJob.query.filter_by(job_seeker_id=seeker.id).order_by(
        SavedJob.created_at.desc()).all()
    return render_template(
        "seeker/saved_jobs.html", saved=saved, title="Saved Jobs")


@bp.route("/save/<int:job_id>", methods=["POST"])
@login_required
@jobseeker_required
def save_job(job_id):
    seeker = current_user.job_seeker
    job = Job.query.get_or_404(job_id)
    existing = SavedJob.query.filter_by(job_seeker_id=seeker.id, job_id=job.id).first()
    if not existing:
        db.session.add(SavedJob(job_seeker_id=seeker.id, job_id=job.id))
        db.session.commit()
        flash("Job saved.", "success")
    else:
        flash("Job already in your saved list.", "info")
    return redirect(request.referrer or url_for("public.jobs"))


@bp.route("/unsave/<int:job_id>", methods=["POST"])
@login_required
@jobseeker_required
def unsave_job(job_id):
    seeker = current_user.job_seeker
    existing = SavedJob.query.filter_by(job_seeker_id=seeker.id, job_id=job_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Job removed from saved list.", "info")
    return redirect(request.referrer or url_for("seeker.saved_jobs"))


@bp.route("/apply/<int:job_id>", methods=["GET", "POST"])
@login_required
@jobseeker_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    seeker = current_user.job_seeker

    if not job.is_public:
        flash("This job is not accepting applications.", "warning")
        return redirect(url_for("public.job_detail", job_id=job.id))

    existing = Application.query.filter_by(job_id=job.id, job_seeker_id=seeker.id).first()
    if existing:
        flash("You have already applied for this job.", "info")
        return redirect(url_for("public.job_detail", job_id=job.id))

    form = ApplicationForm()
    if form.validate_on_submit():
        resume_path = seeker.resume
        if form.resume.data:
            resume_path = save_uploaded_file(
                form.resume.data, "resumes",
                current_app.config["ALLOWED_RESUME_EXTENSIONS"])
        if not resume_path:
            flash("Please upload a resume or add one to your profile first.", "danger")
            return render_template("seeker/apply.html", form=form, job=job,
                                   has_resume=bool(seeker.resume), title="Apply")
        app = Application(
            job_id=job.id, job_seeker_id=seeker.id,
            applicant_id=current_user.id,
            resume=resume_path, cover_letter=form.cover_letter.data,
            status=APP_APPLIED,
        )
        db.session.add(app)
        db.session.commit()
        # Notifications
        notify_jobseeker_application_submitted(current_user.id, job.title)
        notify_employer_new_application(job.employer.user_id, job.title, app.id)
        flash("Your application was submitted successfully!", "success")
        return redirect(url_for("seeker.applications"))
    return render_template(
        "seeker/apply.html", form=form, job=job,
        has_resume=bool(seeker.resume), title=f"Apply for {job.title}",
    )


@bp.route("/notifications")
@login_required
@jobseeker_required
def notifications():
    notes = current_user.notifications
    return render_template(
        "seeker/notifications.html", notifications=notes,
        title="Notifications")


@bp.route("/notifications/mark-read/<int:note_id>", methods=["POST"])
@login_required
def mark_read(note_id):
    note = Notification.query.get_or_404(note_id)
    if note.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    note.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("seeker.notifications"))


@bp.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    for n in current_user.notifications:
        n.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("seeker.notifications"))
