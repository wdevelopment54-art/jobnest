"""Demo/seed data generator. Clearly separated from production data.

Creates realistic development/demo records:
- 1 admin, several employers (each with a Company), several job seekers
- job categories, realistic job postings (PKR salaries), applications,
  saved jobs, a contact message and an admin notification.

Demo credentials are printed at the end and must never be used in production.
"""
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    User, JobSeeker, Employer, Company, Job, JobCategory, Application, SavedJob,
    ContactMessage, Notification,
    ROLE_ADMIN, ROLE_EMPLOYER, ROLE_JOBSEEKER,
    EMPLOYER_APPROVED, JOB_ACTIVE, JOB_PENDING,
    APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW, APP_SELECTED,
)


def seed_data():
    # ---- Categories ----
    categories = [
        "Software Development", "Marketing", "Finance", "Healthcare",
        "Education", "Engineering", "Design", "Sales",
        "Customer Service", "Human Resources",
    ]
    cat_map = {}
    for name in categories:
        c = JobCategory.query.filter_by(name=name).first()
        if not c:
            c = JobCategory(name=name, description=f"{name} opportunities in Pakistan.",
                            is_active=True)
            db.session.add(c)
            db.session.commit()
        cat_map[name] = c

    # ---- Admin ----
    if not User.query.filter_by(email="admin@jobnest.pk").first():
        admin = User(full_name="JOBNEST Administrator",
                     username="admin", email="admin@jobnest.pk",
                     role=ROLE_ADMIN, is_active=True)
        admin.set_password("Admin@12345")
        db.session.add(admin)
        db.session.commit()

    # ---- Employers + Companies ----
    employers_data = [
        ("TechNova Solutions", "Software Development", "51-200",
         "Lahore, Punjab", "Leading software product company building SaaS tools.",
         "info@technova.pk", "0301-1112233", "https://technova.pk"),
        ("Bright Marketing Co", "Marketing", "11-50",
         "Karachi, Sindh", "Full-service digital marketing agency.",
         "hello@brightmarketing.pk", "0302-2223344", "https://brightmarketing.pk"),
        ("MediCare Health", "Healthcare", "201-500",
         "Islamabad, ICT", "Private healthcare provider network.",
         "careers@medicare.pk", "0303-3334455", "https://medicare.pk"),
        ("EduFuture Academy", "Education", "11-50",
         "Faisalabad, Punjab", "Online learning platform for professionals.",
         "jobs@edufuture.pk", "0304-4445566", "https://edufuture.pk"),
        ("FinEdge Capital", "Finance", "51-200",
         "Rawalpindi, Punjab", "Investment and financial advisory firm.",
         "talent@finedge.pk", "0305-5556677", "https://finedge.pk"),
    ]
    employer_objs = []
    for i, (name, ind, size, loc, desc, email, phone, website) in enumerate(employers_data, 1):
        if User.query.filter_by(email=email).first():
            employer_objs.append(Employer.query.filter_by(contact_email=email).first())
            continue
        u = User(full_name=name, username=f"emp{i}", email=email,
                 role=ROLE_EMPLOYER, is_active=True, phone=phone)
        u.set_password("Employer@123")
        db.session.add(u)
        db.session.commit()
        company = Company(
            owner_id=u.id, company_name=name, email=email, phone=phone,
            location=loc, website=website, industry=ind,
            company_size=size, description=desc,
        )
        db.session.add(company)
        db.session.commit()
        e = Employer(user_id=u.id, company_id=company.id, company_name=name,
                    industry=ind, company_size=size, location=loc, description=desc,
                    contact_email=email, phone=phone, website=website,
                    approval_status=EMPLOYER_APPROVED, is_active=True)
        db.session.add(e)
        db.session.commit()
        employer_objs.append(e)

    # ---- Job Seekers ----
    seekers_data = [
        ("Ayesha Khan", "ayesha.khan@email.com", "Lahore, Punjab",
         "Python, Flask, SQL, React", "CS Graduate, 3 years experience."),
        ("Bilal Ahmed", "bilal.ahmed@email.com", "Karachi, Sindh",
         "Java, Spring, AWS", "Backend engineer."),
        ("Fatima Sheikh", "fatima.sheikh@email.com", "Islamabad, ICT",
         "Marketing, SEO, Content", "Digital marketer."),
        ("Usman Tariq", "usman.tariq@email.com", "Rawalpindi, Punjab",
         "Finance, Excel, Analysis", "Financial analyst."),
    ]
    seeker_objs = []
    for i, (name, email, loc, skills, summary) in enumerate(seekers_data, 1):
        if User.query.filter_by(email=email).first():
            seeker_objs.append(
                JobSeeker.query.join(User).filter(User.email == email).first())
            continue
        u = User(full_name=name, username=f"seeker{i}", email=email,
                 role=ROLE_JOBSEEKER, is_active=True, phone=f"030{i}-66677{i}8")
        u.set_password("Seeker@123")
        db.session.add(u)
        db.session.commit()
        s = JobSeeker(user_id=u.id, location=loc, skills=skills,
                      summary=summary, education="Bachelor's Degree")
        db.session.add(s)
        db.session.commit()
        seeker_objs.append(s)

    # ---- Jobs ----
    jobs_data = [
        ("Senior Python Developer", "Software Development", "full_time",
         180000, 280000, "Lahore, Punjab", "3-5 Years",
         "Build scalable web applications using Flask and PostgreSQL.",
         "Python, Flask, SQLAlchemy, REST", "BS in CS", "2026-09-30", True),
        ("Frontend Engineer", "Software Development", "full_time",
         150000, 240000, "Remote", "3-5 Years",
         "Develop responsive UIs with modern frameworks.",
         "JavaScript, React, CSS", "BS in CS", "2026-10-15", True),
        ("Digital Marketing Specialist", "Marketing", "full_time",
         90000, 150000, "Karachi, Sindh", "1-2 Years",
         "Manage campaigns and SEO strategy.",
         "SEO, Google Ads, Analytics", "Marketing Degree", "2026-09-20", False),
        ("Registered Nurse", "Healthcare", "full_time",
         100000, 160000, "Islamabad, ICT", "Entry Level",
         "Provide patient care in clinical settings.",
         "Nursing, Patient Care", "BSN", "2026-11-01", True),
        ("Mathematics Teacher", "Education", "full_time",
         70000, 110000, "Faisalabad, Punjab", "3-5 Years",
         "Teach high school mathematics.",
         "Teaching, Mathematics", "Education Degree", "2026-10-01", False),
        ("Financial Analyst", "Finance", "full_time",
         120000, 190000, "Rawalpindi, Punjab", "1-2 Years",
         "Analyze financial data and prepare reports.",
         "Excel, Finance, Modeling", "Finance Degree", "2026-09-25", True),
        ("UX Designer", "Design", "contract",
         140000, 220000, "Remote", "3-5 Years",
         "Design user-centered product experiences.",
         "Figma, UX Research", "Design Degree", "2026-12-01", False),
        ("Sales Representative", "Sales", "part_time",
         60000, 100000, "Karachi, Sindh", "Entry Level",
         "Drive sales for enterprise software.",
         "Sales, CRM, Communication", "HS Diploma", "2026-08-30", True),
        ("HR Coordinator", "Human Resources", "full_time",
         80000, 130000, "Islamabad, ICT", "1-2 Years",
         "Coordinate recruitment and onboarding.",
         "Recruiting, HRIS", "HR Degree", "2026-10-10", False),
        ("Customer Support Agent", "Customer Service", "internship",
         40000, 70000, "Remote", "Entry Level",
         "Assist customers via chat and email.",
         "Communication, Support", "HS Diploma", "2026-09-15", True),
    ]
    job_objs = []
    for (title, cat, etype, smin, smax, loc, exp, desc, skills, edu, deadline, feat) in jobs_data:
        emp = employer_objs[0] if cat == "Software Development" else \
            employer_objs[min(len(employer_objs) - 1, categories.index(cat) % len(employer_objs))]
        j = Job(employer_id=emp.id, company_id=emp.company_id,
                category_id=cat_map[cat].id,
                title=title, description=desc, skills=skills, education=edu,
                experience=exp, salary=f"PKR {smin:,} - {smax:,}",
                salary_min=smin, salary_max=smax, currency="PKR",
                location=loc, employment_type=etype,
                deadline=datetime.strptime(deadline, "%Y-%m-%d").date(),
                status=JOB_ACTIVE, is_featured=feat)
        db.session.add(j)
        db.session.commit()
        job_objs.append(j)

    # ---- Applications ----
    statuses = [APP_APPLIED, APP_REVIEW, APP_SHORTLISTED, APP_INTERVIEW, APP_SELECTED]
    for i, s in enumerate(seeker_objs):
        if i < len(job_objs):
            j = job_objs[i]
            if not Application.query.filter_by(job_id=j.id, job_seeker_id=s.id).first():
                a = Application(job_id=j.id, job_seeker_id=s.id,
                                applicant_id=s.user_id,
                                status=statuses[i % len(statuses)],
                                cover_letter="I am excited to apply for this role.",
                                applied_at=datetime.utcnow() - timedelta(days=i))
                db.session.add(a)
                db.session.commit()

    # ---- Saved jobs ----
    if seeker_objs and job_objs:
        s = seeker_objs[0]
        for j in job_objs[1:4]:
            if not SavedJob.query.filter_by(job_seeker_id=s.id, job_id=j.id).first():
                db.session.add(SavedJob(job_seeker_id=s.id, job_id=j.id))
        db.session.commit()

    # ---- Contact messages ----
    if not ContactMessage.query.first():
        db.session.add(ContactMessage(
            name="Hassan Ali", email="hassan.ali@email.com", phone="0309-6890020",
            subject="Partnership Inquiry", message="I would like to partner with JOBNEST.",
            status="unread"))
        db.session.commit()

    # ---- Notifications for admin ----
    admin = User.query.filter_by(role=ROLE_ADMIN).first()
    if admin and not admin.notifications:
        db.session.add(Notification(
            user_id=admin.id, title="Welcome",
            message="Admin panel is ready. Manage the platform from here."))
        db.session.commit()

    print("Seed complete: categories, 1 admin, 5 employers+companies, 4 seekers, "
          "10 jobs, applications, saved jobs, messages, notifications.")
    print("DEMO CREDENTIALS (development only):")
    print("  Admin:    admin@jobnest.pk / Admin@12345")
    print("  Employer: info@technova.pk / Employer@123")
    print("  Seeker:   ayesha.khan@email.com / Seeker@123")
