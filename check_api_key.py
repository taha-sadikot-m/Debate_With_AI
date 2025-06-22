print("Starting test...")

import os
print(f"Working directory: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

import sys
print(f"Python version: {sys.version}")

if os.path.exists('.env'):
    try:
        with open('.env', 'r') as f:
            content = f.read()
            print(f"First line of .env: {content.splitlines()[0]}")
    except Exception as e:
        print(f"Error reading .env: {e}")

from dotenv import load_dotenv
print("Loading dotenv...")
load_dotenv(override=True)

api_key = os.environ.get('OPENAI_API_KEY')
print(f"API key loaded: {'Yes' if api_key else 'No'}")

if api_key:
    print(f"API key starts with: {api_key[:10]}")
    
    print("\nTesting OpenAI client...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        print("Client created")
        
        # Try a simple API call
        models = client.models.list()
        print(f"Success! Got {len(models.data)} models")
    except Exception as e:
        print(f"OpenAI error: {str(e)}")
else:
    print("No API key found in environment")
