"""Site-wide settings model (admin-editable).

These settings let the admin control the complete website's branding,
contact details, and social links from the admin panel instead of editing
code or environment variables. Values are stored as key/value rows and
read through :func:`SiteSetting.get_all`.
"""
from app.extensions import db


class SiteSetting(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    label = db.Column(db.String(120), nullable=True)
    group = db.Column(db.String(40), nullable=False, default="general")

    def __repr__(self):
        return f"<SiteSetting {self.key}>"

    @classmethod
    def get_all(cls):
        """Return a dict of all settings keyed by ``key``."""
        return {s.key: s.value for s in cls.query.all()}

    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set_value(cls, key, value, label=None, group="general"):
        """Create or update a single setting."""
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            setting = cls(key=key, group=group)
            db.session.add(setting)
        setting.value = value
        if label is not None:
            setting.label = label
        setting.group = group
        return setting
