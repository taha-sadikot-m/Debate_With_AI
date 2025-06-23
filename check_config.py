import os
import sys
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = ["SECRET_KEY", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    else:
        print("✓ All required environment variables are set")
    return True

def check_imports():
    """Check if all required packages are installed."""
    required_packages = [
        "flask", "flask_sqlalchemy", "flask_login", "flask_socketio", 
        "google.generativeai", "pyttsx3"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"ERROR: Missing packages: {', '.join(missing_packages)}")
        print("Run 'pip install -r requirements.txt' to install all dependencies")
        return False
    else:
        print("✓ All required packages are installed")
    return True

def check_socketio_configuration():
    """Check if SocketIO is configured correctly."""
    try:
        from extensions import socketio
        print("✓ SocketIO import successful")
        return True
    except Exception as e:
        print(f"ERROR with SocketIO configuration: {str(e)}")
        return False

def check_database():
    """Check if database connection works."""
    try:
        from db_init import db
        # Just test connection without creating tables
        print("✓ Database module import successful")
        return True
    except Exception as e:
        print(f"ERROR with database configuration: {str(e)}")
        return False

def perform_checks():
    """Run all checks and return overall status."""
    print("=== Debate App Configuration Check ===")
    all_passed = True
    
    checks = [
        check_environment,
        check_imports,
        check_socketio_configuration,
        check_database
    ]
    
    for check in checks:
        if not check():
            all_passed = False
    
    if all_passed:
        print("\n✓ All checks passed! The application should run correctly.")
    else:
        print("\n✗ Some checks failed. Please fix the issues before deploying.")
    
    return all_passed

if __name__ == "__main__":
    if perform_checks():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Error
