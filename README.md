# Professional Online Job Portal

A full-stack, database-driven job portal built with **Flask** and **SQLite** (PostgreSQL supported for production). It supports three roles — **Job Seeker**, **Employer**, and **Admin** — with strict role-based access control (RBAC), a public job board, authentication with password reset, an approval workflow for employers and jobs, application management, notifications, and a real-data admin dashboard.

---

## Features

### Public Website
- Home, About, Contact pages
- Job board with search, category/type/experience/date filters, sorting, and pagination
- Job detail pages with "Apply" / "Save" actions
- Company directory and company detail pages

### Authentication & Accounts
- Registration for Job Seekers and Employers (with terms acceptance)
- Login with email or username
- Password reset via email (secure signed token, expires)
- Email verification of account existence (no user enumeration)

### Job Seeker Portal
- Dashboard with application stats and recent activity
- Profile management (skills, summary, education, location, resume upload)
- Save / unsave jobs
- Apply to jobs (with resume)
- Track applications and their statuses
- Notifications center

### Employer Portal
- Company profile management (logo upload, description, industry, size, location)
- Post / edit / delete jobs
- Jobs require **admin approval** before going public (configurable)
- Review applications, update statuses (Applied → Reviewing → Shortlisted → Interview → Selected / Rejected)
- Internal notes per application
- Notifications center

### Admin Panel
- Dashboard with real statistics and **Chart.js** charts (jobs by category, applications by status, user growth)
- Manage users (activate/deactivate, delete, role)
- Manage employers (approve / reject / toggle / delete)
- Manage jobs (approve / reject / toggle visibility / delete)
- Manage job categories (CRUD, active toggle)
- Manage applications (view, filter, link to employer review)
- Manage contact messages (mark read, delete)
- Manage notifications (broadcast / delete)

### Security
- Werkzeug password hashing
- Flask-WTF CSRF protection on all forms
- Secure file uploads (extension & size validation, sandboxed upload folder)
- Ownership / authorization checks on every mutating action
- Role-based access decorators (`@admin_required`, `@employer_required`, `@jobseeker_required`)
- Custom error pages (400, 403, 404, 500)

---

## Tech Stack

- **Backend:** Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Mail
- **Database:** SQLite (default, no server needed); PostgreSQL supported for production
- **Frontend:** Jinja2 templates, vanilla CSS, Chart.js (CDN), Font Awesome (CDN)
- **Migrations:** Alembic via Flask-Migrate

---

## Project Structure

```
job portal/
├── app/
│   ├── __init__.py            # Application factory, Jinja globals/filters, error handlers
│   ├── extensions.py          # db, migrate, login_manager, mail, csrf
│   ├── models/                # User, JobSeeker, Employer, Job, JobCategory, Application, SavedJob, ContactMessage, Notification
│   ├── forms/                 # WTForms: auth, profile, job, admin
│   ├── routes/                # Blueprints: public, auth, seeker, employer, admin
│   ├── services/              # email_service, notification_service
│   ├── utils/                 # decorators (RBAC), file_upload, helpers (time_ago, format_date, status_badge_class)
│   ├── scripts/               # seed.py (demo data)
│   ├── static/                # css/style.css, js/main.js, uploads/
│   └── templates/             # base.html, partials/, public/, auth/, seeker/, employer/, admin/, errors/
├── migrations/                # Flask-Migrate / Alembic migrations
├── config.py                  # Config classes (dev/prod/testing)
├── run.py                     # Entry point + CLI commands (create-admin, seed)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### 1. Prerequisites
- Python 3.10+
- SQLite (default; PostgreSQL optional for production)
- A mail account/SMTP credentials for password-reset emails (optional for local testing)

### 2. Clone & create a virtual environment
```bash
cd "job portal"
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```
Key variables:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///job_portal.db   # default; SQLite file in instance/
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@jobportal.com
AUTO_PUBLISH_JOBS=False        # if True, new jobs go live without admin approval
```

> **Switch to PostgreSQL (production):** set `DATABASE_URL=postgresql://user:pass@host/db` (or a Neon cloud URL with `?sslmode=require`) in your `.env`. The string is read from the environment only - no credentials are hardcoded in source, and `.env` is gitignored.

### 5. Database setup (migrations)
```bash
# Tell Flask where the app entry point is
set FLASK_APP=run.py            # Windows cmd
# export FLASK_APP=run.py       # macOS / Linux

flask db upgrade               # applies the initial migration (creates all tables)
```
If you ever need to regenerate migrations from scratch: `flask db migrate -m "message"` then `flask db upgrade`.

### 6. Create the admin account
```bash
flask create-admin
```
Follow the prompts (email, username, full name, password). The command is **safe** — it refuses to create duplicates and validates password length.

### 7. (Optional) Seed demo data
```bash
flask seed
```
Creates sample categories, employers, job seekers, jobs, applications, saved jobs, messages, and notifications.

**Demo accounts after seeding:**
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@jobnest.pk | Admin@12345 |
| Employer | info@technova.pk | Employer@123 |
| Job Seeker | ayesha.khan@email.com | Seeker@123 |

---

## Running the App

```bash
# Development server
flask run
# or
python run.py
```
Open http://localhost:5000

---

## Testing the Routes

A smoke test exercises the real database end-to-end (public routes, login for all three roles, job posting, search, apply, save, and contact). It uses the DATABASE_URL from your .env (SQLite by default):

```bash
# from the project root, with the venv active
python smoke_test.py
```
It prints an HTTP status code for each route/flow and writes details to _smoke_result.txt. All logins and flows should succeed (200/302) and rows should appear in the database.

---

## Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (pbkdf2:sha256).
- All forms are protected by CSRF tokens.
- Uploads are restricted to allowed extensions and a max size; files are stored outside the template path.
- Every protected action checks both authentication and authorization (role + ownership).
- Password-reset tokens are signed with `itsdangerous` and expire.

---

## License

This project is provided as a demonstration/learning resource.
"# jobnest"  
