import google.generativeai as genai
from db_init import app
import os
import json
from datetime import datetime
import time
import pyttsx3
import threading

# Configure Gemini with API key directly from environment
import dotenv
# Reload environment variables to ensure we get the latest values
dotenv.load_dotenv(override=True)
api_key = os.environ.get('GEMINI_API_KEY')

# Initialize Gemini with API key
if api_key:
    genai.configure(api_key=api_key)
    print(f"Gemini API initialized with API key starting with: {api_key[:15]}...")
else:
    print("WARNING: No Gemini API key found in environment variables!")

# Initialize pyttsx3
engine = pyttsx3.init()
# Set properties
engine.setProperty('rate', 180)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

def generate_debate_response(topic, position, history):
    prompt = f"""
    [ROLE] You are a world-class debater arguing the {position} position.
    [TOPIC] Debate topic: "{topic}"
    [HISTORY] Previous arguments:
    {format_history(history[-4:])}
    
    [TASK] Craft a compelling response that:
    1. Directly addresses the last point made
    2. Uses logical reasoning and evidence
    3. Includes rhetorical techniques (anaphora, tricolon, etc.)    4. Maintains a passionate but professional tone
    5. Is 2-3 sentences maximum
      [RESPONSE]
    """
    
    try:
        # Get the model name from app config
        # model_name = app.config['DEBATE_MODEL']
        model_name = 'gemini-2.0-flash'  # Default to a widely available model
        print(f"Using debate model: {model_name}")
        
        # Check if API key is set
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("WARNING: Gemini API key not found in environment variables")
            return "No API key found. Please set a valid GEMINI_API_KEY in your environment."
            
        # Re-configure Gemini with API key to ensure it's set properly
        genai.configure(api_key=api_key)
        print(f"Configured Gemini API with key starting with: {api_key[:8]}...")
        
        # Create and configure the model
        model = genai.GenerativeModel(model_name)
        
        # Generate response
        generation_config = genai.types.GenerationConfig(
            temperature=0.8,
            max_output_tokens=200,
            top_p=0.95,
            top_k=40
        )
          # Define safety settings to avoid content filtering issues
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT", 
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", 
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT", 
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
        
        print(f"Sending prompt to Gemini model '{model_name}'...")
        response = model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
        
        argument = response.text.strip()
        print(f"Successfully received response from Gemini")
        return argument
    except Exception as e:
        error_message = str(e)
        print(f"Error generating debate response: {error_message}")
        print(f"API key: {api_key[:5]}...{api_key[-4:] if api_key and len(api_key) > 10 else 'None'}")
        print(f"Model name: {model_name}")
        
        # Provide more detailed error message based on the exception
        if "not found" in error_message.lower():
            print(f"Model '{model_name}' not found or not available with your API key")
            return "I'm having trouble accessing the AI model. Please check that your API key has access to the specified model. Error details: " + error_message
        elif "authent" in error_message.lower() or "api key" in error_message.lower():
            print("Authentication error with the Gemini API")
            return "Authentication error with the Gemini API. Please check that your API key is valid."
        elif "content" in error_message.lower() and "safety" in error_message.lower():
            print("Content filtered by safety settings")
            return "The response was blocked by Gemini's content safety filters. Please try again with different debate content."
        else:
            print(f"Unknown error: {error_message}")
            return "I'm having trouble forming a response. Technical details: " + error_message

def evaluate_performance(transcript):
    user_args = [msg['text'] for msg in transcript if msg['speaker'] == 'user']
    
    prompt = f"""
    [ROLE] You are a professional debate judge analyzing a debate performance.
    [CRITERIA] Evaluate based on:
    - Logical consistency (30%)
    - Evidence quality (25%)
    - Rebuttal effectiveness (20%)
    - Persuasiveness (15%)
    - Rhetorical skill (10%)
    
    [TASK] Provide:
    1. Numerical score (0-100) with breakdown
    2. Three specific strengths
    3. Three actionable improvements
    4. Analysis of 2 key arguments with suggestions
    5. Overall remarks
    
    [DEBATE TRANSCRIPT]
    {json.dumps(user_args, indent=2)}
    
    [RESPONSE FORMAT]
    Score: [number]/100
    Breakdown: [JSON]
    Strengths:
    - [strength1]
    - [strength2]
    - [strength3]
      Improvements:
    - [improvement1]
    - [improvement2]
    - [improvement3]
    
    Argument Analysis:
    1. Argument: "[excerpt]"
       Feedback: [specific feedback]
       Suggestion: [specific suggestion]
    
    2. Argument: "[excerpt]"
       Feedback: [specific feedback]
       Suggestion: [specific suggestion]
      Final Remarks: [overall feedback]
    """
    
    try:
        # Get the model name from app config
        #model_name = app.config['DEBATE_MODEL']
        model_name = 'gemini-2.0-flash'
        print(f"Using evaluation model: {model_name}")
        
        # Check if API key is set
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("WARNING: Gemini API key not found in environment variables")
            return "No API key found. Please set a valid GEMINI_API_KEY in your environment."
            
        # Re-configure Gemini with API key to ensure it's set properly
        genai.configure(api_key=api_key)
        print(f"Configured Gemini API with key starting with: {api_key[:8]}...")
        
        # Create and configure the model
        model = genai.GenerativeModel(model_name)
        
        # If transcript is too long, truncate it
        if len(prompt) > 30000:
            print("Prompt too long, truncating...")
            prompt = prompt[:30000]
            
        # Generate response with more lenient settings
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=600,
            top_p=0.95,
            top_k=40
        )
        
        print(f"Sending evaluation prompt to Gemini model '{model_name}'...")
        print(f"Prompt length: {len(prompt)} characters")
          # Try with more permissive safety settings
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT", 
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", 
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT", 
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
        
        response = model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
        
        print(f"Successfully received evaluation from Gemini")
        return response.text.strip()
    except Exception as e:
        error_message = str(e)
        print(f"Error generating evaluation: {error_message}")
        print(f"API key: {api_key[:5]}...{api_key[-4:] if api_key and len(api_key) > 10 else 'None'}")
        print(f"Model name: {model_name}")
        
        # Provide more detailed error message based on the exception
        if "not found" in error_message.lower():
            print(f"Model '{model_name}' not found or not available with your API key")
            return "I'm having trouble accessing the AI model for evaluation. Please check that your API key has access to the model 'gemini-pro'. Error details: " + error_message
        elif "authent" in error_message.lower() or "api key" in error_message.lower():
            print("Authentication error with the Gemini API")
            return "Authentication error with the Gemini API. Please check that your API key is valid."
        elif "content" in error_message.lower() and "safety" in error_message.lower():
            print("Content filtered by safety settings")
            return "The evaluation was blocked by Gemini's content safety filters. Please try again with different debate content."
        elif "length" in error_message.lower() or "token" in error_message.lower():
            print("Input too long for model")
            return "The debate transcript is too long for the model to process. Please try a shorter debate or break it into segments."
        else:
            print(f"Unknown error: {error_message}")
            return "I'm unable to evaluate the debate at this time. Technical details: " + error_message

def generate_tts(text):
    """Generate and save TTS audio with natural pauses"""
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    
    # Add natural pauses by inserting commas and periods
    text_with_pauses = text
    
    filename = f"static/audio/tts_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
    
    # Generate speech with pyttsx3
    try:
        # We'll use a thread to prevent blocking since pyttsx3 can block
        def save_speech():
            engine.save_to_file(text_with_pauses, filename)
            engine.runAndWait()
            
        thread = threading.Thread(target=save_speech)
        thread.start()
        thread.join(timeout=10)  # Wait up to 10 seconds
            
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        # Create an empty file as fallback
        with open(filename, 'wb') as f:
            f.write(b'')
        
    return filename

def format_history(history):
    return "\n".join([
        f"{msg['speaker'].upper()}: {msg['text']}" 
        for msg in history
    ])