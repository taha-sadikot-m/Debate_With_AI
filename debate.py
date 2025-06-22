from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from db_init import db, socketio
from models import Debate
from ai_utils import generate_debate_response, evaluate_performance, generate_tts
import json
from datetime import datetime

debate_bp = Blueprint('debate', __name__)

@debate_bp.route('/start', methods=['POST'])
@login_required
def start_debate():
    # Handle both JSON and form data
    if request.is_json:
        data = request.json
    else:
        data = request.form
    
    # Check if required data is present
    if not data.get('topic') or not data.get('user_position') or not data.get('first_speaker'):
        return jsonify({'error': 'Missing required fields'}), 400
        
    debate = Debate(
        topic=data['topic'],
        user_position=data['user_position'],
        ai_position='for' if data['user_position'] == 'against' else 'against',
        user_id=current_user.id
    )
    
    # Add initial message
    transcript = []
    if data['first_speaker'] == 'ai':
        ai_response = generate_debate_response(
            debate.topic, 
            debate.ai_position,
            transcript
        )
        audio_file = generate_tts(ai_response)
        transcript.append({
            'speaker': 'ai',
            'text': ai_response,
            'audio': audio_file,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    debate.set_transcript(transcript)
    db.session.add(debate)
    db.session.commit()
    
    return jsonify({
        'debate_id': debate.id,
        'transcript': transcript
    })

@debate_bp.route('/submit', methods=['POST'])
@login_required
def submit_argument():
    # Handle both JSON and form data
    if request.is_json:
        data = request.json
    else:
        data = request.form
        
    # Check if required data is present
    if not data.get('debate_id') or not data.get('argument'):
        return jsonify({'error': 'Missing required fields'}), 400
        
    debate = Debate.query.get(data['debate_id'])
    
    # Add user argument
    transcript = debate.get_transcript()
    transcript.append({
        'speaker': 'user',
        'text': data['argument'],
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Generate AI response
    ai_response = generate_debate_response(
        debate.topic,
        debate.ai_position,
        transcript
    )
    
    # Generate TTS and save audio
    audio_file = generate_tts(ai_response)
    
    transcript.append({
        'speaker': 'ai',
        'text': ai_response,
        'audio': audio_file,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    debate.set_transcript(transcript)
    db.session.commit()
    
    # Emit real-time response through SocketIO
    socketio.emit('ai_response', {
        'debate_id': debate.id,
        'text': ai_response,
        'audio_url': audio_file
    }, room=f'debate_{debate.id}')
    
    return jsonify({
        'ai_response': ai_response,
        'audio_url': audio_file,
        'transcript': transcript
    })

@debate_bp.route('/evaluate/<int:debate_id>', methods=['GET'])
@login_required
def evaluate_debate(debate_id):
    debate = Debate.query.get_or_404(debate_id)
    if debate.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    evaluation = evaluate_performance(debate.get_transcript())
    debate.evaluation = json.dumps(evaluation)
    db.session.commit()
    
    return jsonify(evaluation)