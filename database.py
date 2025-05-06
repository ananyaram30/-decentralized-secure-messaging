from models import db
from flask_sqlalchemy import SQLAlchemy

def init_db(app):
    """Initialize the database for the application."""
    db.init_app(app)
    
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")