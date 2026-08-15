"""Admin management forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email

from app.models import ROLE_JOBSEEKER, ROLE_EMPLOYER, ROLE_ADMIN


class UserForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    role = SelectField(
        "Role",
        choices=[
            (ROLE_JOBSEEKER, "Job Seeker"),
            (ROLE_EMPLOYER, "Employer"),
            (ROLE_ADMIN, "Admin"),
        ],
        validators=[DataRequired()],
    )
    is_active = BooleanField("Active")
    submit = SubmitField("Save User")


class AdminJobForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired(), Length(max=200)])
    location = StringField("Location", validators=[DataRequired(), Length(max=120)])
    employment_type = StringField("Employment Type", validators=[DataRequired(), Length(max=30)])
    salary = StringField("Salary", validators=[Optional(), Length(max=100)])
    status = SelectField("Status", validators=[DataRequired()])
    submit = SubmitField("Save Job")
