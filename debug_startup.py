
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        print("App initialized successfully.")
        # Try to access a model
        from app.models import User
        print(f"User model loaded: {User}")
except Exception as e:
    print(f"Startup Error: {e}")
    import traceback
    traceback.print_exc()
