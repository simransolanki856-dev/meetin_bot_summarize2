import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meetings.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    
    # AI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')  # openai or gemini
    
    # Google Meet Bot Configuration
    GOOGLE_ACCOUNT_EMAIL = os.getenv('GOOGLE_ACCOUNT_EMAIL')
    GOOGLE_ACCOUNT_PASSWORD = os.getenv('GOOGLE_ACCOUNT_PASSWORD')