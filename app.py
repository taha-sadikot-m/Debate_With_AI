from db_init import app, db, socketio

# Import models first to ensure they're registered
from models import User

# Set up login user loader
from extensions import login
from models import load_user

@login.user_loader
def user_loader(id):
    return User.query.get(int(id))

# Register blueprints
from auth import auth_bp
from debate import debate_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(debate_bp, url_prefix='/debate')

# Import routes
from routes import *

# For gunicorn deployment
application = app

if __name__ == '__main__':
    # Use debug mode only in development
    socketio.run(app, debug=app.config.get('DEBUG', True), host='0.0.0.0')