from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with Flask app
    """
    db.init_app(app)

    # Optional: test DB connection on startup
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ PostgreSQL database connected")
        except Exception as e:
            print("❌ Database connection failed:", e)
