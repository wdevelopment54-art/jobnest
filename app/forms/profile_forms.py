"""Profile and resume forms for job seekers and employers."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SubmitField, SelectField, FileField as _FileField,
)
from wtforms.validators import DataRequired, Length, Optional, URL

from app.models import EMPLOYMENT_TYPES, EXPERIENCE_LEVELS


class JobSeekerProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Length(max=150)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    location = StringField("Location", validators=[Optional(), Length(max=120)])
    profile_picture = FileField(
        "Profile Picture",
        validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Images only.")],
    )
    summary = TextAreaField("Professional Summary", validators=[Optional(), Length(max=2000)])
    education = TextAreaField("Education", validators=[Optional(), Length(max=2000)])
    skills = TextAreaField("Skills (comma separated)", validators=[Optional(), Length(max=2000)])
    experience = TextAreaField("Work Experience", validators=[Optional(), Length(max=3000)])
    certifications = TextAreaField("Certifications", validators=[Optional(), Length(max=2000)])
    languages = TextAreaField("Languages", validators=[Optional(), Length(max=500)])
    resume = FileField(
        "Resume / CV (PDF, DOC, DOCX)",
        validators=[Optional(), FileAllowed(["pdf", "doc", "docx"], "Documents only.")],
    )
    submit = SubmitField("Save Changes")


class EmployerProfileForm(FlaskForm):
    company_name = StringField("Company Name", validators=[DataRequired(), Length(max=150)])
    company_logo = FileField(
        "Company Logo", validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Images only.")]
    )
    industry = StringField("Industry", validators=[Optional(), Length(max=100)])
    company_size = SelectField(
        "Company Size",
        choices=[
            ("", "Select size"),
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("201-500", "201-500 employees"),
            ("501-1000", "501-1000 employees"),
            ("1000+", "1000+ employees"),
        ],
        validators=[Optional()],
    )
    location = StringField("Location", validators=[Optional(), Length(max=120)])
    website = StringField("Website", validators=[Optional(), URL(), Length(max=200)])
    contact_email = StringField("Contact Email", validators=[Optional(), Length(max=150)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    description = TextAreaField("Company Description", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Save Company Profile")
