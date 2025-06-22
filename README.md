# AI Platform Debate

A debate platform where users can practice debate skills by arguing with an AI opponent powered by Google's Gemini AI.

## Features

- Debate with an AI opponent on various topics
- Choose to argue "for" or "against" a position
- Real-time AI responses
- Text-to-speech for AI arguments
- Performance evaluation and feedback
- User authentication and debate history

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secret_key
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Initialize the database: `python db_init.py`
5. Run the application: `flask run` or `python app.py`

## Getting a Gemini API Key

1. Visit the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file as `GEMINI_API_KEY=your_api_key`

## Usage

1. Register or login to your account
2. Start a new debate by selecting a topic and your position
3. Engage in a back-and-forth debate with the AI
4. Get feedback and evaluation on your performance

## Technology Stack

- Backend: Flask, SQLAlchemy
- AI: Google Gemini API
- Frontend: HTML, CSS, JavaScript
- Text-to-Speech: pyttsx3
