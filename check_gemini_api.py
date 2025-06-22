import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get('GEMINI_API_KEY')

if api_key:
    print(f"Found Gemini API key starting with: {api_key[:5]}...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Test with a simple prompt
    model = genai.GenerativeModel('gemini-pro')
    
    try:
        response = model.generate_content("Say hello and confirm you're working correctly")
        print("\nAPI Response:")
        print(response.text)
        print("\nGemini API is working correctly!")
    except Exception as e:
        print(f"\nError when testing Gemini API: {str(e)}")
else:
    print("ERROR: No Gemini API key found in environment variables!")
    print("Please add your Gemini API key to the .env file as GEMINI_API_KEY=your_api_key")
