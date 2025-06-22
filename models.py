from db_init import db
from flask_login import UserMixin
from datetime import datetime
import json
from extensions import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    google_id = db.Column(db.String(128), unique=True)
    debates = db.relationship('Debate', backref='user', lazy='dynamic')

class Debate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200))
    user_position = db.Column(db.String(10))  # 'for' or 'against'
    ai_position = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transcript = db.Column(db.Text)
    evaluation = db.Column(db.Text)
    
    def get_transcript(self):
        return json.loads(self.transcript) if self.transcript else []
    
    def set_transcript(self, data):
        self.transcript = json.dumps(data)

def load_user(id):
    return User.query.get(int(id))