"""Authentication blueprint."""
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, current_app,
)
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import (
    User, JobSeeker, Employer,
    ROLE_JOBSEEKER, ROLE_EMPLOYER, ROLE_ADMIN,
    EMPLOYER_PENDING,
)
from app.forms import (
    RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,
)
from app.services import (
    send_password_reset_email, verify_reset_token, notify_admin_new_employer,
)

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data,
            role=form.account_type.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        if user.role == ROLE_JOBSEEKER:
            seeker = JobSeeker(user_id=user.id)
            db.session.add(seeker)
            db.session.commit()
            flash("Job seeker account created! Complete your profile to stand out.", "success")
        elif user.role == ROLE_EMPLOYER:
            employer = Employer(
                user_id=user.id,
                company_name=user.full_name,
                approval_status=EMPLOYER_PENDING,
            )
            db.session.add(employer)
            db.session.commit()
            notify_admin_new_employer(employer.company_name)
            flash("Employer account created! Set up your company profile. "
                  "Your account is pending admin approval.", "info")

        login_user(user)
        return redirect_after_login(user)
    return render_template("auth/register.html", form=form, title="Sign Up")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Contact support.", "danger")
                return render_template("auth/login.html", form=form, title="Login")
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect_after_login(user)
        flash("Invalid email/username or password.", "danger")
    return render_template("auth/login.html", form=form, title="Login")


def redirect_after_login(user):
    if user.role == ROLE_ADMIN:
        return redirect(url_for("admin.dashboard"))
    if user.role == ROLE_EMPLOYER:
        return redirect(url_for("employer.dashboard"))
    return redirect(url_for("seeker.dashboard"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.index"))


@bp.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            send_password_reset_email(user)
        # Always show the same message to avoid user enumeration
        flash("If an account exists for that email, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_request.html", form=form, title="Forgot Password")


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))
    user = verify_reset_token(token)
    if not user:
        flash("That reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_token.html", form=form, title="Reset Password")
