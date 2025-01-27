import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the application"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Tesseract Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.getenv('MONGODB_DB', 'ingredient_analyzer')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Image Processing Configuration
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # Analysis Configuration
    CACHE_TIMEOUT = 3600  # 1 hour
    MAX_RETRIES = 3
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        
        if not cls.OPENAI_API_KEY:
            missing.append('OPENAI_API_KEY')
        
        if not os.path.exists(cls.TESSERACT_PATH):
            missing.append('TESSERACT_PATH (valid path)')
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key':
            missing.append('SECRET_KEY (secure value)')
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
