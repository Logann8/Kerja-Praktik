from app import create_app, db
from app.models.user import User

app = create_app('default')

with app.app_context():
    # Only creates tables that don't exist
    db.create_all()
    print("Database tables updated successfully!")
    print("Users table created (if it didn't exist).")
