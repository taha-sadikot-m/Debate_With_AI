import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the client
api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# List available models
models = genai.list_models()
print("Available models:")
for model in models:
    print(f"- {model.name}: {model.supported_generation_methods}")
