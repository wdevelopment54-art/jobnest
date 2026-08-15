"""Application entry point."""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402

app = create_app(os.environ.get("FLASK_ENV", "default"))


@app.cli.command("create-admin")
def create_admin():
    """Create the first administrator account (safe initialization)."""
    from app.extensions import db
    from app.models import User, ROLE_ADMIN
    import getpass

    email = input("Admin email: ").strip().lower()
    if User.query.filter_by(email=email).first():
        print("A user with that email already exists.")
        return
    username = input("Admin username: ").strip()
    if User.query.filter_by(username=username).first():
        print("A user with that username already exists.")
        return
    full_name = input("Full name: ").strip() or "Administrator"
    password = getpass.getpass("Admin password: ")
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        return
    user = User(full_name=full_name, username=username, email=email,
                role=ROLE_ADMIN, is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Admin user '{username}' created successfully.")


@app.cli.command("seed")
def seed():
    """Populate the database with realistic demo data."""
    from app.scripts.seed import seed_data
    seed_data()
    print("Seed data created.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
