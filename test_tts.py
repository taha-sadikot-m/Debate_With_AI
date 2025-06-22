import pyttsx3
import os
from datetime import datetime

def test_tts():
    # Initialize pyttsx3
    engine = pyttsx3.init()
    
    # Set properties
    engine.setProperty('rate', 180)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    # Create audio directory if it doesn't exist
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    
    # Test text
    text = "This is a test of the text to speech system. It should work correctly now."
    
    # Generate filename
    filename = f"static/audio/test_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
    
    print(f"Generating audio file: {filename}")
    
    # Save to file
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
    print(f"Audio file generated: {filename}")
    
    return filename

if __name__ == "__main__":
    test_tts()
