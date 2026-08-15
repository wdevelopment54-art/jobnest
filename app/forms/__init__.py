"""Forms package."""
from app.forms.auth_forms import (
    RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,
)
from app.forms.profile_forms import JobSeekerProfileForm, EmployerProfileForm
from app.forms.job_forms import (
    JobForm, ApplicationForm, ContactForm, CategoryForm, ApplicationStatusForm,
)
from app.forms.admin_forms import UserForm, AdminJobForm

__all__ = [
    "RegistrationForm", "LoginForm", "RequestResetForm", "ResetPasswordForm",
    "JobSeekerProfileForm", "EmployerProfileForm",
    "JobForm", "ApplicationForm", "ContactForm", "CategoryForm", "ApplicationStatusForm",
    "UserForm", "AdminJobForm",
]
