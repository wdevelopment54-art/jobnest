"""Authentication-related forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField,
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp, ValidationError,
)
from app.models import User, ROLE_JOBSEEKER, ROLE_EMPLOYER


class RegistrationForm(FlaskForm):
    full_name = StringField(
        "Full Name", validators=[DataRequired(), Length(min=2, max=150)]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Username may only contain letters, numbers and underscores.",
            ),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    phone = StringField("Phone", validators=[Length(max=30)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    account_type = SelectField(
        "Account Type",
        choices=[(ROLE_JOBSEEKER, "Job Seeker"), (ROLE_EMPLOYER, "Employer")],
        validators=[DataRequired()],
    )
    terms = BooleanField(
        "I agree to the Terms and Conditions", validators=[DataRequired()]
    )
    submit = SubmitField("Create Account")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("That username is already taken.")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError("That email is already registered.")


class LoginForm(FlaskForm):
    identifier = StringField(
        "Email or Username", validators=[DataRequired(), Length(max=150)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8)],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Reset Password")
