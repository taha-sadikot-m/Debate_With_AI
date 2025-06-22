from flask import Flask
from config import Config
from extensions import db, socketio, init_extensions

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
init_extensions(app)
