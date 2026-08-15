"""Admin panel blueprint."""
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort, current_app,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    User, JobSeeker, Employer, Job, JobCategory, Application, ContactMessage,
    Notification, JOB_ACTIVE, JOB_APPROVED, JOB_REJECTED, JOB_PENDING,
    JOB_INACTIVE, JOB_EXPIRED, EMPLOYER_APPROVED, EMPLOYER_REJECTED,
    EMPLOYER_PENDING, ROLE_ADMIN,
)
from app.forms import UserForm, CategoryForm, AdminJobForm
from app.services import (
    notify_employer_job_approved, notify_employer_job_rejected,
)
from app.utils.decorators import admin_required

bp = Blueprint("admin", __name__)


@bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_seekers = User.query.filter_by(role="jobseeker").count()
    total_employers = User.query.filter_by(role="employer").count()
    total_companies = Employer.query.count()
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(status=JOB_ACTIVE).count()
    pending_jobs = Job.query.filter_by(status=JOB_PENDING).count()
    total_apps = Application.query.count()
    pending_apps = Application.query.filter_by(status="Applied").count()
    messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(status="unread").count()

    # Charts data
    jobs_by_cat = [
        [name, int(cnt)]
        for name, cnt in db.session.query(JobCategory.name, db.func.count(Job.id))
        .join(Job, Job.category_id == JobCategory.id)
        .group_by(JobCategory.name).all()
    ]
    apps_by_status = [
        [status, int(cnt)]
        for status, cnt in db.session.query(Application.status, db.func.count(Application.id))
        .group_by(Application.status).all()
    ]
    # User growth (last 6 months)
    from datetime import datetime, timedelta
    growth = []
    for i in range(5, -1, -1):
        d = datetime.utcnow() - timedelta(days=30 * i)
        start = d.replace(day=1)
        if i == 0:
            end = datetime.utcnow()
        else:
            end = (start.replace(month=start.month % 12 + 1, year=start.year + (start.month // 12)) if start.month != 12 else start.replace(year=start.year + 1, month=1))
        cnt = User.query.filter(User.created_at >= start, User.created_at < end).count()
        growth.append((start.strftime("%b"), cnt))

    stats = {
        "total_users": total_users, "total_seekers": total_seekers,
        "total_employers": total_employers, "total_companies": total_companies,
        "total_jobs": total_jobs, "active_jobs": active_jobs,
        "pending_jobs": pending_jobs, "total_apps": total_apps,
        "pending_apps": pending_apps, "messages": messages,
        "unread_messages": unread_messages,
    }
    return render_template(
        "admin/dashboard.html", stats=stats,
        jobs_by_cat=jobs_by_cat, apps_by_status=apps_by_status,
        growth=growth, title="Admin Dashboard",
    )


# ---------------- Users ----------------
@bp.route("/users")
@login_required
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    query = User.query
    role = request.args.get("role", "").strip()
    search = request.args.get("search", "").strip()
    if role:
        query = query.filter_by(role=role)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (User.username.ilike(like)) | (User.email.ilike(like)) |
            (User.full_name.ilike(like)))
    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    return render_template("admin/users.html", users=pagination.items,
                           pagination=pagination, current_role=role,
                           search=search, title="Users")


@bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data, role=form.role.data,
            is_active=form.is_active.data,
        )
        user.set_password("ChangeMe123!")
        db.session.add(user)
        db.session.commit()
        if user.role == "jobseeker":
            db.session.add(JobSeeker(user_id=user.id))
        elif user.role == "employer":
            db.session.add(Employer(user_id=user.id,
                                    company_name=user.full_name,
                                    approval_status=EMPLOYER_APPROVED))
        db.session.commit()
        flash("User created. Default password is 'ChangeMe123!'.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, title="Add User")


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.full_name = form.full_name.data.strip()
        user.username = form.username.data.strip()
        user.email = form.email.data.strip().lower()
        user.phone = form.phone.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, user=user,
                           title="Edit User")


@bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.users"))
    user.is_active = not user.is_active
    db.session.commit()
    flash("User status updated.", "info")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "info")
    return redirect(url_for("admin.users"))


# ---------------- Employers ----------------
@bp.route("/employers")
@login_required
@admin_required
def employers():
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()
    query = Employer.query
    if status:
        query = query.filter_by(approval_status=status)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Employer.company_name.ilike(like)) |
            (Employer.industry.ilike(like)))
    employers = query.order_by(Employer.created_at.desc()).all()
    return render_template("admin/employers.html", employers=employers,
                           current_status=status, search=search,
                           statuses=[EMPLOYER_PENDING, EMPLOYER_APPROVED, EMPLOYER_REJECTED],
                           title="Employers")


@bp.route("/employers/<int:emp_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_employer(emp_id):
    emp = Employer.query.get_or_404(emp_id)
    emp.approval_status = EMPLOYER_APPROVED
    emp.is_active = True
    db.session.commit()
    flash("Employer approved.", "success")
    return redirect(url_for("admin.employers"))


@bp.route("/employers/<int:emp_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_employer(emp_id):
    emp = Employer.query.get_or_404(emp_id)
    emp.approval_status = EMPLOYER_REJECTED
    db.session.commit()
    flash("Employer rejected.", "info")
    return redirect(url_for("admin.employers"))


@bp.route("/employers/<int:emp_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_employer(emp_id):
    emp = Employer.query.get_or_404(emp_id)
    emp.is_active = not emp.is_active
    db.session.commit()
    flash("Employer status updated.", "info")
    return redirect(url_for("admin.employers"))


@bp.route("/employers/<int:emp_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_employer(emp_id):
    emp = Employer.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employer deleted.", "info")
    return redirect(url_for("admin.employers"))


# ---------------- Jobs ----------------
@bp.route("/jobs")
@login_required
@admin_required
def jobs():
    page = request.args.get("page", 1, type=int)
    query = Job.query
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()
    if status:
        query = query.filter_by(status=status)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Job.title.ilike(like)) | (Job.location.ilike(like)))
    query = query.order_by(Job.created_at.desc())
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    return render_template("admin/jobs.html", jobs=pagination.items,
                           pagination=pagination, current_status=status,
                           search=search,
                           statuses=[JOB_PENDING, JOB_APPROVED, JOB_REJECTED,
                                     JOB_ACTIVE, JOB_INACTIVE, JOB_EXPIRED],
                           title="Jobs")


@bp.route("/jobs/<int:job_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = JOB_ACTIVE
    db.session.commit()
    notify_employer_job_approved(job.employer.user_id, job.title)
    flash("Job approved and published.", "success")
    return redirect(url_for("admin.jobs"))


@bp.route("/jobs/<int:job_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = JOB_REJECTED
    db.session.commit()
    notify_employer_job_rejected(job.employer.user_id, job.title)
    flash("Job rejected.", "info")
    return redirect(url_for("admin.jobs"))


@bp.route("/jobs/<int:job_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status == JOB_ACTIVE:
        job.status = JOB_INACTIVE
    elif job.status == JOB_INACTIVE:
        job.status = JOB_ACTIVE
    else:
        flash("Only active/inactive jobs can be toggled.", "warning")
        return redirect(url_for("admin.jobs"))
    db.session.commit()
    flash("Job status updated.", "info")
    return redirect(url_for("admin.jobs"))


@bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "info")
    return redirect(url_for("admin.jobs"))


# ---------------- Categories ----------------
@bp.route("/categories")
@login_required
@admin_required
def categories():
    cats = JobCategory.query.order_by(JobCategory.name).all()
    return render_template("admin/categories.html", categories=cats,
                           title="Categories")


@bp.route("/categories/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        if JobCategory.query.filter_by(name=form.name.data.strip()).first():
            flash("A category with that name already exists.", "warning")
            return render_template("admin/category_form.html", form=form,
                                   title="Add Category")
        db.session.add(JobCategory(
            name=form.name.data.strip(), description=form.description.data))
        db.session.commit()
        flash("Category created.", "success")
        return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", form=form,
                           title="Add Category")


@bp.route("/categories/<int:cat_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_category(cat_id):
    cat = JobCategory.query.get_or_404(cat_id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        if (JobCategory.query.filter_by(name=form.name.data.strip()).first()
                and cat.name != form.name.data.strip()):
            flash("A category with that name already exists.", "warning")
            return render_template("admin/category_form.html", form=form,
                                   cat=cat, title="Edit Category")
        cat.name = form.name.data.strip()
        cat.description = form.description.data
        db.session.commit()
        flash("Category updated.", "success")
        return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", form=form, cat=cat,
                           title="Edit Category")


@bp.route("/categories/<int:cat_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_category(cat_id):
    cat = JobCategory.query.get_or_404(cat_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    flash("Category status updated.", "info")
    return redirect(url_for("admin.categories"))


@bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(cat_id):
    cat = JobCategory.query.get_or_404(cat_id)
    if cat.jobs:
        flash("Cannot delete a category that has jobs. Deactivate it instead.", "warning")
        return redirect(url_for("admin.categories"))
    db.session.delete(cat)
    db.session.commit()
    flash("Category deleted.", "info")
    return redirect(url_for("admin.categories"))


# ---------------- Applications ----------------
@bp.route("/applications")
@login_required
@admin_required
def applications():
    page = request.args.get("page", 1, type=int)
    query = Application.query
    status = request.args.get("status", "").strip()
    job_id = request.args.get("job_id", type=int)
    employer_id = request.args.get("employer_id", type=int)
    if status:
        query = query.filter_by(status=status)
    if job_id:
        query = query.filter_by(job_id=job_id)
    if employer_id:
        query = query.join(Job).filter(Job.employer_id == employer_id)
    query = query.order_by(Application.applied_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    jobs = Job.query.order_by(Job.title).all()
    employers = Employer.query.order_by(Employer.company_name).all()
    return render_template("admin/applications.html",
                           applications=pagination.items,
                           pagination=pagination, current_status=status,
                           current_job=job_id, current_employer=employer_id,
                           jobs=jobs, employers=employers,
                           statuses=["Applied", "Under Review", "Shortlisted",
                                     "Interview", "Selected", "Rejected"],
                           title="Applications")


# ---------------- Contact Messages ----------------
@bp.route("/messages")
@login_required
@admin_required
def messages():
    status = request.args.get("status", "").strip()
    query = ContactMessage.query
    if status:
        query = query.filter_by(status=status)
    msgs = query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=msgs,
                           current_status=status, title="Contact Messages")


@bp.route("/messages/<int:msg_id>/toggle-read", methods=["POST"])
@login_required
@admin_required
def toggle_message_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.status = "read" if msg.status == "unread" else "unread"
    db.session.commit()
    return redirect(url_for("admin.messages"))


@bp.route("/messages/<int:msg_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.", "info")
    return redirect(url_for("admin.messages"))


# ---------------- Notifications ----------------
@bp.route("/notifications")
@login_required
@admin_required
def notifications():
    notes = current_user.notifications
    return render_template("admin/notifications.html", notifications=notes,
                           title="Notifications")


# ---------------- Site Settings ----------------
@bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def settings():
    """Admin-editable site-wide settings (branding, contact, social)."""
    from app.forms import SiteSettingsForm
    from app.models import SiteSetting

    form = SiteSettingsForm()
    if form.validate_on_submit():
        for field in form:
            if field.name in ("csrf_token", "submit"):
                continue
            SiteSetting.set_value(
                key=field.name,
                value=field.data or "",
                label=field.label.text,
                group="site",
            )
        db.session.commit()
        flash("Site settings saved successfully.", "success")
        return redirect(url_for("admin.settings"))

    # Pre-populate the form from stored settings (fall back to config).
    if not form.is_submitted():
        stored = SiteSetting.get_all()
        for field in form:
            if field.name in ("csrf_token", "submit"):
                continue
            if field.name in stored and stored[field.name] is not None:
                field.data = stored[field.name]
            else:
                field.data = current_app.config.get(field.name, "")
    return render_template("admin/settings.html", form=form, title="Site Settings")
