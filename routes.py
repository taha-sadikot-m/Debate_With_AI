from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from db_init import app
from models import Debate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's debate history
    debates = current_user.debates.order_by(Debate.created_at.desc()).all()
    return render_template('dashboard.html', debates=debates)

@app.route('/debate')
@login_required
def debate():
    return render_template('debate.html')

@app.route('/history/<int:debate_id>')
@login_required
def debate_history(debate_id):
    debate = Debate.query.get_or_404(debate_id)
    if debate.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    return render_template('history.html', debate=debate)

@app.route('/ai_config')
@login_required
def ai_config():
    config = {
        'debate_model': app.config['DEBATE_MODEL'],
        'api_key_set': bool(app.config['GEMINI_API_KEY'])
    }
    return render_template('ai_config.html', config=config)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth/register.html')