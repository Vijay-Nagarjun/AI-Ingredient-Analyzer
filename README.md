# IngredientAI - Food Ingredient Analyzer

A web application that analyzes food product ingredients using OCR and AI to determine their health impact and provides detailed insights about ingredient categories.

## Features

- **Smart OCR**: Advanced image processing to accurately extract ingredients from photos
- **AI-Powered Analysis**: Uses OpenAI GPT-4 to analyze ingredients and their health impacts
- **Multiple Input Methods**: 
  - Text input
  - Camera capture with image cropping
  - File upload
- **Detailed Analysis**:
  - Ingredient categorization
  - Health score calculation
  - Percentage breakdown
  - Natural vs. artificial ingredient analysis
- **Product Comparison**: Compare two products side by side
- **History Tracking**: View past analyses with timestamps
- **User Authentication**: Secure login system with user and admin roles
- **Mobile Responsive**: Works seamlessly on all devices

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **OCR**: Tesseract with OpenCV
- **AI**: OpenAI GPT-4 API
- **Image Processing**: PIL, OpenCV

## Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR installed on your system
3. MongoDB installed and running
4. OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd IngredientAI
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
MONGODB_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
TESSERACT_PATH=path_to_tesseract_executable
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
IngredientAI/
├── services/               # Core services
│   ├── ocr_service.py     # OCR and image processing
│   ├── ingredient_service.py  # Ingredient analysis
│   └── config.py          # Configuration management
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── img/              # Images
├── templates/             # HTML templates
├── models.py             # Database models
├── app.py               # Main application
└── requirements.txt     # Python dependencies
```

## Demo Credentials

- **Regular User**:
  - Username: user
  - Password: user
- **Admin User**:
  - Username: admin
  - Password: admin

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| MONGODB_URI | MongoDB connection string | Yes |
| SECRET_KEY | Flask secret key | Yes |
| OPENAI_API_KEY | OpenAI API key | Yes |
| TESSERACT_PATH | Path to Tesseract executable | Yes |
| DEBUG | Enable debug mode | No |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
