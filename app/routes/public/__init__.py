"""Public website blueprint."""
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, current_app,
)
from flask_login import current_user

from app.extensions import db
from app.models import (
    Job, Employer, JobCategory, Application, SavedJob, ContactMessage,
    JOB_ACTIVE, EMPLOYER_APPROVED,
)
from app.forms import ContactForm
from app.services import notify_admin_new_message
from app.utils import save_uploaded_file

bp = Blueprint("public", __name__)


def _public_jobs_query():
    """Return a base query for publicly visible jobs."""
    from datetime import datetime
    return Job.query.filter(
        Job.status == JOB_ACTIVE,
        (Job.deadline.is_(None)) | (Job.deadline >= datetime.utcnow().date()),
    )


@bp.route("/")
def index():
    featured_jobs = (
        _public_jobs_query().filter(Job.is_featured == True)  # noqa: E712
        .order_by(Job.created_at.desc()).limit(6).all()
    )
    latest_jobs = _public_jobs_query().order_by(Job.created_at.desc()).limit(8).all()
    categories = JobCategory.query.filter_by(is_active=True).all()
    companies = (
        Employer.query.filter_by(approval_status=EMPLOYER_APPROVED, is_active=True)
        .order_by(Employer.id.desc()).limit(8).all()
    )
    # Stats
    stats = {
        "jobs": _public_jobs_query().count(),
        "companies": Employer.query.filter_by(
            approval_status=EMPLOYER_APPROVED, is_active=True).count(),
        "seekers": 0,
        "applications": 0,
    }
    from app.models import User
    stats["seekers"] = User.query.filter_by(role="jobseeker").count()
    stats["applications"] = Application.query.count()
    return render_template(
        "public/index.html",
        featured_jobs=featured_jobs, latest_jobs=latest_jobs,
        categories=categories, companies=companies, stats=stats,
        title="Find Your Dream Job",
    )


@bp.route("/jobs")
def jobs():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["PER_PAGE"]

    query = _public_jobs_query()

    keyword = request.args.get("keyword", "").strip()
    location = request.args.get("location", "").strip()
    category_id = request.args.get("category", type=int)
    employment_type = request.args.get("employment_type", "").strip()
    experience = request.args.get("experience", "").strip()
    date_posted = request.args.get("date_posted", "").strip()
    sort = request.args.get("sort", "latest")

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (Job.title.ilike(like)) |
            (Job.location.ilike(like)) |
            (Job.skills.ilike(like))
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if category_id:
        query = query.filter(Job.category_id == category_id)
    if employment_type:
        query = query.filter(Job.employment_type == employment_type)
    if experience:
        query = query.filter(Job.experience == experience)
    if date_posted:
        from datetime import datetime, timedelta
        days = {"today": 1, "3days": 3, "week": 7, "month": 30}.get(date_posted)
        if days:
            since = datetime.utcnow().date() - timedelta(days=days)
            query = query.filter(Job.created_at >= since)

    if sort == "oldest":
        query = query.order_by(Job.created_at.asc())
    elif sort == "salary_low":
        query = query.order_by(Job.salary.asc())
    elif sort == "salary_high":
        query = query.order_by(Job.salary.desc())
    else:
        query = query.order_by(Job.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = JobCategory.query.filter_by(is_active=True).all()
    saved_ids = set()
    if current_user.is_authenticated and current_user.is_jobseeker:
        saved_ids = {s.job_id for s in current_user.job_seeker.saved_jobs}
    return render_template(
        "public/jobs.html", jobs=pagination.items, pagination=pagination,
        categories=categories, saved_ids=saved_ids,
        EMPLOYMENT_TYPES=["Full Time", "Part Time", "Internship", "Contract", "Remote"],
        EXPERIENCE_LEVELS=["Entry Level", "1-2 Years", "3-5 Years", "5-8 Years", "8+ Years"],
        title="Browse Jobs",
    )


@bp.route("/job/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    if not job.is_public:
        abort(404)
    already_applied = False
    is_saved = False
    if current_user.is_authenticated and current_user.is_jobseeker:
        seeker = current_user.job_seeker
        already_applied = Application.query.filter_by(
            job_id=job.id, job_seeker_id=seeker.id).first() is not None
        is_saved = SavedJob.query.filter_by(
            job_id=job.id, job_seeker_id=seeker.id).first() is not None
    related = _public_jobs_query().filter(
        Job.category_id == job.category_id, Job.id != job.id).limit(4).all()
    return render_template(
        "public/job_detail.html", job=job, already_applied=already_applied,
        is_saved=is_saved, related_jobs=related, title=job.title,
    )


@bp.route("/companies")
def companies():
    page = request.args.get("page", 1, type=int)
    per_page = 9
    query = Employer.query.filter_by(approval_status=EMPLOYER_APPROVED, is_active=True)
    keyword = request.args.get("keyword", "").strip()
    location = request.args.get("location", "").strip()
    industry = request.args.get("industry", "").strip()
    if keyword:
        query = query.filter(
            (Employer.company_name.ilike(f"%{keyword}%")) |
            (Employer.industry.ilike(f"%{keyword}%"))
        )
    if location:
        query = query.filter(Employer.location.ilike(f"%{location}%"))
    if industry:
        query = query.filter(Employer.industry == industry)
    query = query.order_by(Employer.company_name.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    industries = [i[0] for i in db.session.query(Employer.industry).distinct()
                  if i[0]]
    return render_template(
        "public/companies.html", companies=pagination.items,
        pagination=pagination, industries=industries, title="Companies",
    )


@bp.route("/company/<int:employer_id>")
def company_detail(employer_id):
    employer = Employer.query.get_or_404(employer_id)
    if employer.approval_status != EMPLOYER_APPROVED or not employer.is_active:
        abort(404)
    company_jobs = (
        _public_jobs_query().filter(Job.employer_id == employer.id)
        .order_by(Job.created_at.desc()).all()
    )
    return render_template(
        "public/company_detail.html", employer=employer,
        company_jobs=company_jobs, title=employer.company_name,
    )


@bp.route("/about")
def about():
    return render_template("public/about.html", title="About Us")


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data.strip(), email=form.email.data.strip().lower(),
            phone=form.phone.data, subject=form.subject.data.strip(),
            message=form.message.data.strip(),
        )
        db.session.add(msg)
        db.session.commit()
        notify_admin_new_message(msg.name, msg.subject)
        flash("Thank you for contacting us! We will get back to you soon.", "success")
        return redirect(url_for("public.contact"))
    return render_template("public/contact.html", form=form, title="Contact Us")


@bp.route("/search")
def search():
    return redirect(url_for("public.jobs", **request.args))
