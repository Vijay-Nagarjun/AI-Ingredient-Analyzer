# Setup Guide for AI Ingredient Analyzer

This guide will help you set up the AI Ingredient Analyzer project on your local machine.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **MongoDB** installed locally (or access to MongoDB Atlas)
3. **Tesseract OCR** engine installed on your system
   - Windows: Download and install from [GitHub Tesseract Release](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add Tesseract to your system PATH

## Step-by-Step Setup

### 1. Create Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# For Windows
venv\Scripts\activate
# For Unix/MacOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Additional Required Packages
Install these if not already included in requirements.txt:
```bash
pip install python-dotenv pymongo[srv] bcrypt Pillow pytesseract Flask Werkzeug
```

### 4. Environment Setup
Create a `.env` file in the root directory with these variables:
```
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional for now
```

### 5. MongoDB Setup

#### Local MongoDB Setup
1. Install MongoDB Community Edition
2. Start MongoDB service
3. The application will automatically create the required database and collections

#### Creating Initial Data
Run the following script to create dummy data:

```python
# Save as setup_dummy_data.py
from models import User, Admin, IngredientAnalysis
from db_config import DatabaseConfig
import bcrypt

def create_dummy_data():
    db_config = DatabaseConfig()
    db = db_config.get_db()
    
    # Clear existing data
    db.users.delete_many({})
    db.admins.delete_many({})
    db.ingredient_analyses.delete_many({})
    
    # Create dummy user
    hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
    dummy_user = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': hashed_password,
        'created_at': datetime.now()
    }
    db.users.insert_one(dummy_user)
    
    # Create dummy admin
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    dummy_admin = {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': admin_password,
        'created_at': datetime.now()
    }
    db.admins.insert_one(dummy_admin)
    
    # Create dummy analyses
    dummy_analyses = [
        {
            'user_id': dummy_user['_id'],
            'image_path': 'testing_images/sample1.jpg',
            'ingredients_text': 'Water, Sugar, Salt, Natural Flavors',
            'analysis_result': {
                'safe_ingredients': ['Water', 'Salt'],
                'caution_ingredients': ['Sugar'],
                'unknown_ingredients': ['Natural Flavors']
            },
            'created_at': datetime.now()
        },
        {
            'user_id': dummy_user['_id'],
            'image_path': 'testing_images/sample2.jpg',
            'ingredients_text': 'Milk, Cocoa, Vanilla Extract',
            'analysis_result': {
                'safe_ingredients': ['Milk', 'Vanilla Extract'],
                'caution_ingredients': [],
                'unknown_ingredients': ['Cocoa']
            },
            'created_at': datetime.now()
        }
    ]
    db.ingredient_analyses.insert_many(dummy_analyses)
    
    print("Dummy data created successfully!")
    db_config.close()

if __name__ == '__main__':
    create_dummy_data()
```

### 6. Test Images Setup
1. Create a `testing_images` directory in the project root
2. Add some sample food product images with visible ingredient lists
3. Sample images should be clear and contain readable ingredient text

### 7. Running the Application
```bash
# Make sure your virtual environment is activated
python app.py
```

The application will be available at `http://localhost:5000`

### Default Login Credentials
```
Regular User:
Username: testuser
Password: password123

Admin User:
Username: admin
Password: admin123
```

## Common Issues and Solutions

### 1. MongoDB Connection Issues
- Ensure MongoDB service is running
- Check if the MongoDB URI in `.env` is correct
- For Windows users, MongoDB service can be started from Services app

### 2. Tesseract OCR Issues
- Ensure Tesseract is properly installed
- Verify PATH environment variable includes Tesseract
- For Windows users, typical path: `C:\Program Files\Tesseract-OCR`

### 3. Image Processing Issues
- Ensure Pillow and OpenCV are properly installed
- Check if testing_images directory exists and has proper permissions

## Testing the Setup

1. Login with the dummy user credentials
2. Upload a test image from the testing_images directory
3. Try the ingredient analysis feature
4. Check the history page for saved analyses

## Need Help?
If you encounter any issues:
1. Check the console for error messages
2. Verify all environment variables are set correctly
3. Ensure all prerequisites are installed
4. Contact the team lead for additional support
