"""Admin management forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email, URL

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


class SiteSettingsForm(FlaskForm):
    """Admin-editable site-wide settings (branding, contact, social)."""

    # General / branding
    SITE_NAME = StringField("Site Name", validators=[DataRequired(), Length(max=80)])
    SITE_EMAIL = StringField("Contact Email", validators=[Optional(), Email(), Length(max=150)])

    # Contact
    SITE_PHONE_DISPLAY = StringField("Phone (display)", validators=[Optional(), Length(max=40)])
    SITE_PHONE_HREF = StringField("Phone (link, e.g. tel:0300...)", validators=[Optional(), Length(max=60)])
    SITE_WHATSAPP_NUMBER = StringField("WhatsApp Number (display)", validators=[Optional(), Length(max=40)])
    SITE_WHATSAPP_HREF = StringField("WhatsApp Link", validators=[Optional(), Length(max=120)])
    SITE_WHATSAPP_MESSAGE = TextAreaField("WhatsApp Default Message", validators=[Optional(), Length(max=300)])
    SITE_ADDRESS = StringField("Address", validators=[Optional(), Length(max=200)])
    SITE_CITY = StringField("City", validators=[Optional(), Length(max=80)])
    SITE_STATE = StringField("State/Province", validators=[Optional(), Length(max=80)])
    SITE_COUNTRY = StringField("Country", validators=[Optional(), Length(max=80)])
    SITE_MAP_URL = StringField("Google Maps URL", validators=[Optional(), URL(), Length(max=400)])

    # Social
    SITE_FACEBOOK_URL = StringField("Facebook URL", validators=[Optional(), URL(), Length(max=200)])
    SITE_TWITTER_URL = StringField("Twitter URL", validators=[Optional(), URL(), Length(max=200)])
    SITE_LINKEDIN_URL = StringField("LinkedIn URL", validators=[Optional(), URL(), Length(max=200)])
    SITE_INSTAGRAM_URL = StringField("Instagram URL", validators=[Optional(), URL(), Length(max=200)])

    submit = SubmitField("Save Settings")
