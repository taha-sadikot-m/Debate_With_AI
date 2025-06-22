from db_init import db, app
import os

# Import all models to ensure they're registered
from models import User, Debate

def init_db():
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create all tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
