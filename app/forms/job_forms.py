"""Job posting, application, contact and admin forms."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SubmitField, SelectField, DateField, IntegerField,
)
from wtforms.validators import DataRequired, Length, Optional

from app.models import EMPLOYMENT_TYPES, EMPLOYMENT_TYPE_LABELS, EXPERIENCE_LEVELS


class JobForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired(), Length(max=200)])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    description = TextAreaField("Job Description", validators=[DataRequired(), Length(min=20)])
    responsibilities = TextAreaField("Responsibilities", validators=[Optional(), Length(max=3000)])
    requirements = TextAreaField("Requirements", validators=[Optional(), Length(max=3000)])
    skills = TextAreaField("Required Skills (comma separated)", validators=[Optional(), Length(max=1000)])
    education = StringField("Education", validators=[Optional(), Length(max=200)])
    experience = SelectField(
        "Experience Level",
        choices=[("", "Select level")] + [(e, e) for e in EXPERIENCE_LEVELS],
        validators=[Optional()],
    )
    salary_min = IntegerField("Minimum Salary", validators=[Optional()])
    salary_max = IntegerField("Maximum Salary", validators=[Optional()])
    salary = StringField("Salary Display (e.g. PKR 50,000 - 70,000)", validators=[Optional(), Length(max=100)])
    location = StringField("Location", validators=[DataRequired(), Length(max=120)])
    employment_type = SelectField(
        "Employment Type",
        choices=[(e, EMPLOYMENT_TYPE_LABELS[e]) for e in EMPLOYMENT_TYPES],
        validators=[DataRequired()],
    )
    deadline = DateField("Application Deadline", validators=[Optional()])
    benefits = TextAreaField("Benefits", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Post Job")


class ApplicationForm(FlaskForm):
    resume = FileField(
        "Upload Resume (optional if you already have one)",
        validators=[Optional(), FileAllowed(["pdf", "doc", "docx"], "Documents only.")],
    )
    cover_letter = TextAreaField("Cover Letter", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Submit Application")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Length(max=150)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=200)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10)])
    submit = SubmitField("Send Message")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save Category")


class ApplicationStatusForm(FlaskForm):
    status = SelectField("Status", validators=[DataRequired()])
    interview_date = DateField("Interview Date", validators=[Optional()])
    interview_time = StringField("Interview Time", validators=[Optional(), Length(max=20)])
    interview_notes = TextAreaField("Interview Notes", validators=[Optional(), Length(max=2000)])
    employer_notes = TextAreaField("Employer Notes", validators=[Optional(), Length(max=2000)])
    rejection_reason = TextAreaField("Rejection Reason", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Update Application")
