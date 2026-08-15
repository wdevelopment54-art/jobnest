"""Shared helper functions and template filters."""
from datetime import datetime


def time_ago(dt):
    """Return a human-friendly 'time ago' string for a datetime."""
    if not dt:
        return ""
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{int(hours)} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 30:
        return f"{int(days)} day{'s' if days != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{int(months)} month{'s' if months != 1 else ''} ago"
    years = months // 12
    return f"{int(years)} year{'s' if years != 1 else ''} ago"


def format_date(value, fmt="%b %d, %Y"):
    if not value:
        return "—"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(fmt)


def status_badge_class(status):
    """Map an application/job status to a Bootstrap-ish badge class."""
    mapping = {
        "Applied": "badge-applied",
        "Under Review": "badge-review",
        "Shortlisted": "badge-shortlisted",
        "Interview": "badge-interview",
        "Selected": "badge-selected",
        "Rejected": "badge-rejected",
        "pending": "badge-pending",
        "approved": "badge-selected",
        "rejected": "badge-rejected",
        "active": "badge-selected",
        "inactive": "badge-review",
        "expired": "badge-rejected",
    }
    return mapping.get(status, "badge-secondary")
