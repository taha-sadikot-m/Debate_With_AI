from flask import Blueprint, redirect, url_for, request, flash, session, render_template, jsonify
from flask_login import login_user, logout_user, current_user
from models import User
from db_init import db
from extensions import oauth
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Log the user in
    login_user(user)
    
    return jsonify({'success': True, 'redirect': url_for('dashboard')})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Find the user
    user = User.query.filter_by(email=data['email']).first()
    
    # Check password
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Log the user in
    remember = data.get('remember', False)
    login_user(user, remember=remember)
    
    return jsonify({'success': True, 'redirect': url_for('dashboard')})

@auth_bp.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    user = User.query.filter_by(google_id=user_info['id']).first()
    if not user:
        user = User(
            username=user_info['email'],
            email=user_info['email'],
            google_id=user_info['id']
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('dashboard'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))