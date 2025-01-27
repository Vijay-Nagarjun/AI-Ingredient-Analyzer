# AI Ingredient Analyzer

## Project Overview
The AI Ingredient Analyzer is an advanced web application that helps users analyze food product ingredients using OCR (Optical Character Recognition) and AI technologies. The system can extract ingredients from product images, analyze their safety, and provide detailed information about each ingredient.

## Technology Stack

### Backend Framework
- **Flask** (v2.3.3): A lightweight Python web framework that provides the foundation for our application
- **Werkzeug** (v2.3.7): WSGI web application library used by Flask for request handling

### Database
- **MongoDB**: NoSQL database used for storing user data, analysis history, and ingredient information
- **PyMongo** (v4.6.1): MongoDB driver for Python, enabling database operations

### Authentication & Security
- **bcrypt** (v4.1.2): For secure password hashing
- **python-dotenv** (v0.19.0): For managing environment variables and sensitive configurations

### Image Processing & OCR
- **Pillow** (v10.1.0): Python Imaging Library for image processing and manipulation
- **pytesseract** (v0.3.10): Python wrapper for Google's Tesseract-OCR Engine
- **OpenCV** (planned): For advanced image preprocessing

### AI & Machine Learning
- **OpenAI API** (v1.0.0): Integration with OpenAI's language models for ingredient analysis
- Future integrations planned:
  - Advanced OCR capabilities
  - Custom trained models for ingredient classification

### Frontend
- **HTML/CSS/JavaScript**: For the web interface
- **Bootstrap**: For responsive design and UI components
- Static file structure in `/static` directory
- Template rendering using Jinja2 (Flask's template engine)

### Development & Testing
- **pytest**: For unit and integration testing
- **pyngrok** (v7.2.2): For tunnel testing and development

## Project Structure
```
AI-Ingredient-Analyzer/
├── app.py                 # Main Flask application file
├── models.py             # Database models and schemas
├── ingredient_analyzer.py # Core analysis logic
├── db_config.py          # Database configuration
├── requirements.txt      # Python dependencies
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── tests/              # Test files
└── scripts/            # Utility scripts
```

## Key Features
1. **User Authentication**
   - Secure login/signup system
   - Role-based access control (Users and Admins)

2. **Image Processing**
   - Image upload and preprocessing
   - OCR text extraction from product images
   - Image enhancement for better OCR results

3. **Ingredient Analysis**
   - AI-powered ingredient identification
   - Safety assessment of ingredients
   - Detailed ingredient information
   - Comparison between different products

4. **History and Management**
   - Analysis history tracking
   - User dashboard
   - Admin panel for system monitoring

## API Integration

### OpenAI Integration (Planned)
The system will utilize OpenAI's API for:
- Natural language processing of ingredient lists
- Detailed ingredient analysis
- Safety assessments
- Alternative ingredient suggestions

Example API usage:
```python
import openai

async def analyze_ingredients(ingredient_list):
    response = await openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in food ingredients analysis."},
            {"role": "user", "content": f"Analyze these ingredients: {ingredient_list}"}
        ]
    )
    return response.choices[0].message.content
```

### OCR Implementation
Currently using Tesseract OCR with plans to enhance accuracy:
```python
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    # Preprocessing steps
    enhanced = ImageEnhance.Contrast(image).enhance(1.5)
    # OCR extraction
    text = pytesseract.image_to_string(enhanced)
    return text
```

## Security Considerations
- Environment variables for sensitive data
- Secure password hashing
- Input validation and sanitization
- CSRF protection
- Secure file upload handling

## Future Enhancements
1. Advanced OCR capabilities with multiple engine support
2. Real-time ingredient analysis
3. Mobile application development
4. Ingredient alternative suggestions
5. Nutritional information analysis
6. Community features and user reviews
7. API endpoint for third-party integration

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Install Tesseract OCR engine
5. Set up MongoDB database
6. Run the application: `python app.py`

## Environment Variables
Required environment variables in `.env`:
```
MONGODB_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
```

## Contributing
Guidelines for contributing to the project:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## License
[Your chosen license]
