"""End-to-end smoke test against the REAL PostgreSQL database (Neon).

Uses the DATABASE_URL from .env (no SQLite override). Tests public routes,
login for each role (single shared client with logout between users, which
mirrors a real browser and avoids Flask-Login cross-client session leakage),
and core flows: job posting, search, apply, save, contact.
Results are written to _smoke_result.txt for reliable inspection.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import (User, Job, JobCategory, Application, SavedJob,
                         ContactMessage, Company, JOB_ACTIVE)

app = create_app("default")
app.config["WTF_CSRF_ENABLED"] = False

DEMO = {
    "admin": ("admin@jobnest.pk", "Admin@12345", "/admin/dashboard"),
    "employer": ("info@technova.pk", "Employer@123", "/employer/dashboard"),
    "seeker": ("ayesha.khan@email.com", "Seeker@123", "/seeker/dashboard"),
}

results = []


def log(msg):
    results.append(str(msg))
    print(msg)


def do_login(client, email, password):
    # Ensure clean session before logging in
    client.get("/auth/logout", follow_redirects=True)
    return client.post("/auth/login", data={"identifier": email, "password": password},
                       follow_redirects=False)


with app.app_context():
    log("DB: " + app.config["SQLALCHEMY_DATABASE_URI"][:45] + " ...")

    c = app.test_client()
    for r in ["/", "/jobs", "/companies", "/about", "/contact",
              "/auth/login", "/auth/register"]:
        log(f"public {r} -> {c.get(r).status_code}")

    # Login each role on the SAME client (logout between to mimic browser)
    for role, (email, pw, dash) in DEMO.items():
        resp = do_login(c, email, pw)
        loc = resp.headers.get("Location")
        log(f"{role} login -> {resp.status_code} (loc={loc})")
        d = c.get(dash, follow_redirects=False)
        log(f"  {dash} -> {d.status_code}")

    # Job search
    log(f"job search -> {c.get('/jobs?q=developer&location=Lahore').status_code}")

    # Employer posts a job
    do_login(c, *DEMO["employer"][:2])
    cat = JobCategory.query.filter_by(name="Software Development").first()
    new_job = {
        "title": "QA Automation Engineer",
        "category_id": str(cat.id),
        "description": "Write end-to-end tests for our platform using pytest and Selenium.",
        "location": "Lahore, Punjab",
        "employment_type": "full_time",
        "salary_min": "120000",
        "salary_max": "180000",
        "salary": "PKR 120,000 - 180,000",
    }
    r = c.post("/employer/jobs/new", data=new_job, follow_redirects=False)
    log(f"employer post job -> {r.status_code}")
    created = Job.query.filter_by(title="QA Automation Engineer").first()
    log(f"  job in DB: {bool(created)} id={created.id if created else None}")

    # Seeker applies to an ACTIVE seeded job (pending jobs correctly reject applications)
    do_login(c, *DEMO["seeker"][:2])
    seeker_user = User.query.filter_by(email=DEMO["seeker"][0]).first()
    sk = seeker_user.job_seeker
    sk.resume = "resumes/smoke_dummy.pdf"
    db.session.commit()
    active_job = Job.query.filter_by(status=JOB_ACTIVE).first()
    if active_job:
        r = c.post(f"/seeker/apply/{active_job.id}",
                   data={"cover_letter": "I am very interested in this role."},
                   follow_redirects=False)
        log(f"seeker apply (job {active_job.id}) -> {r.status_code}")
        app_rec = Application.query.filter_by(job_id=active_job.id, job_seeker_id=sk.id).first()
        log(f"  application in DB: {bool(app_rec)} applicant_id={app_rec.applicant_id if app_rec else None}")
    else:
        log("seeker apply -> SKIPPED (no active job found)")

    # Seeker saves the freshly posted job
    if created:
        r = c.post(f"/seeker/save/{created.id}", follow_redirects=False)
        log(f"seeker save job -> {r.status_code}")
        saved = SavedJob.query.filter_by(job_id=created.id).first()
        log(f"  saved in DB: {bool(saved)}")

    # Contact form
    r = c.post("/contact", data={
        "name": "Test User", "email": "test.user@example.com",
        "phone": "0300-1234567", "subject": "Demo Inquiry",
        "message": "This is a smoke test contact submission.",
    }, follow_redirects=False)
    log(f"contact submit -> {r.status_code}")
    msg = ContactMessage.query.filter_by(email="test.user@example.com").first()
    log(f"  contact in DB: {bool(msg)}")

    # Counts
    log("\nDB COUNTS:")
    for name, model in [("users", User), ("companies", Company), ("jobs", Job),
                        ("applications", Application), ("saved_jobs", SavedJob),
                        ("contact_messages", ContactMessage)]:
        log(f"  {name}: {db.session.query(model).count()}")

with open("_smoke_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
log("\nSMOKE TEST COMPLETE")
