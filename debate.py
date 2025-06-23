from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from db_init import db, socketio
from models import Debate
from ai_utils import generate_debate_response, evaluate_performance, generate_tts
import json
import re
from datetime import datetime

debate_bp = Blueprint('debate', __name__)

def parse_evaluation(evaluation_text):
    """
    Parse the evaluation text from the AI into structured data
    """
    if isinstance(evaluation_text, dict):
        # Already parsed
        return evaluation_text
        
    result = {
        'score': 0,
        'breakdown': {},
        'strengths': [],
        'improvements': [],
        'argument_analysis': [],
        'final_remarks': ''
    }
    
    try:
        # Extract score (0-100)
        score_match = re.search(r'Score: (\d+)/100', evaluation_text)
        if score_match:
            result['score'] = int(score_match.group(1))
            
        # Extract breakdown JSON
        breakdown_match = re.search(r'Breakdown: ({.*?})', evaluation_text, re.DOTALL)
        if breakdown_match:
            try:
                breakdown_str = breakdown_match.group(1)
                # Try to parse as is
                try:
                    result['breakdown'] = json.loads(breakdown_str)
                except:
                    # Clean up the string and try again
                    cleaned_str = re.sub(r"'([^']+)':", r'"\1":', breakdown_str)
                    result['breakdown'] = json.loads(cleaned_str)
            except Exception as e:
                print(f"Error parsing breakdown: {str(e)}")
                
        # Extract strengths
        strengths_section = re.search(r'Strengths:(.*?)Improvements:', evaluation_text, re.DOTALL)
        if strengths_section:
            strengths_text = strengths_section.group(1)
            strengths = re.findall(r'-\s+(.*?)$', strengths_text, re.MULTILINE)
            result['strengths'] = [s.strip() for s in strengths if s.strip()]
            
        # Extract improvements
        improvements_section = re.search(r'Improvements:(.*?)Argument Analysis:', evaluation_text, re.DOTALL)
        if improvements_section:
            improvements_text = improvements_section.group(1)
            improvements = re.findall(r'-\s+(.*?)$', improvements_text, re.MULTILINE)
            result['improvements'] = [s.strip() for s in improvements if s.strip()]
            
        # Extract argument analysis
        arguments = []
        arg_pattern = r'\d+\.\s+Argument:\s+"([^"]+)"\s+Feedback:\s+(.*?)\s+Suggestion:\s+(.*?)(?=\d+\.\s+Argument:|Final Remarks:|$)'
        for match in re.finditer(arg_pattern, evaluation_text, re.DOTALL):
            arguments.append({
                'excerpt': match.group(1).strip(),
                'feedback': match.group(2).strip(),
                'suggestion': match.group(3).strip()
            })
        result['argument_analysis'] = arguments
        
        # Extract final remarks
        remarks_match = re.search(r'Final Remarks:\s+(.*?)$', evaluation_text, re.DOTALL)
        if remarks_match:
            result['final_remarks'] = remarks_match.group(1).strip()
            
        return result
    except Exception as e:
        print(f"Error parsing evaluation: {str(e)}")
        return result

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
    try:
        print(f"Starting evaluation for debate ID: {debate_id}")
        debate = Debate.query.get_or_404(debate_id)
        
        if debate.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if request is for JSON (API) or HTML (web view)
        wants_json = request.headers.get('Accept', '').find('application/json') > -1 or request.args.get('format') == 'json'
            
        # Check if evaluation already exists
        if debate.evaluation and not request.args.get('regenerate'):
            evaluation_data = json.loads(debate.evaluation)
            
            if wants_json:
                return jsonify({'evaluation': evaluation_data})
            else:
                parsed_evaluation = parse_evaluation(evaluation_data)
                return render_template('evaluation.html', 
                                      debate=debate, 
                                      evaluation=evaluation_data,
                                      score=parsed_evaluation['score'],
                                      breakdown=parsed_evaluation['breakdown'],
                                      strengths=parsed_evaluation['strengths'],
                                      improvements=parsed_evaluation['improvements'],
                                      argument_analysis=parsed_evaluation['argument_analysis'],
                                      final_remarks=parsed_evaluation['final_remarks'])
        
        transcript = debate.get_transcript()
        print(f"Retrieved transcript with {len(transcript)} entries")
        
        # Ensure we have enough content to evaluate
        if len(transcript) < 2:
            error_msg = 'Debate is too short to evaluate. Add more arguments first.'
            if wants_json:
                return jsonify({'error': error_msg}), 400
            else:
                return render_template('evaluation.html', debate=debate, error=error_msg)
            
        print("Calling evaluate_performance function...")
        evaluation = evaluate_performance(transcript)
        print(f"Received evaluation result of length {len(evaluation)}")
        
        # Check if we got an error message back
        if evaluation.startswith("I'm having trouble") or evaluation.startswith("Authentication error"):
            print(f"Evaluation returned error: {evaluation[:100]}...")
            if wants_json:
                return jsonify({'error': evaluation}), 500
            else:
                return render_template('evaluation.html', debate=debate, error=evaluation)
            
        # Save the evaluation
        debate.evaluation = json.dumps(evaluation)
        db.session.commit()
        print(f"Saved evaluation to database for debate ID: {debate_id}")
        
        # Parse the evaluation text into structured data
        parsed_evaluation = parse_evaluation(evaluation)
        
        if wants_json:
            return jsonify({'evaluation': evaluation})
        else:
            return render_template('evaluation.html', 
                                  debate=debate, 
                                  evaluation=evaluation,
                                  score=parsed_evaluation['score'],
                                  breakdown=parsed_evaluation['breakdown'],
                                  strengths=parsed_evaluation['strengths'],
                                  improvements=parsed_evaluation['improvements'],
                                  argument_analysis=parsed_evaluation['argument_analysis'],
                                  final_remarks=parsed_evaluation['final_remarks'])
    except Exception as e:
        error_msg = f"Error in evaluate_debate: {str(e)}"
        print(error_msg)
        if request.headers.get('Accept', '').find('application/json') > -1 or request.args.get('format') == 'json':
            return jsonify({'error': error_msg}), 500
        else:
            return render_template('evaluation.html', debate=debate, error=error_msg)