# IngredientAI - Food Ingredient Analyzer

A web application that analyzes food product ingredients to determine their health impact and provides detailed insights about ingredient categories.

## Features

- **Ingredient Analysis**: Scan or input ingredients to get health scores and detailed breakdowns
- **Product Comparison**: Compare two products side by side
- **History Tracking**: View past analyses with timestamps
- **User Authentication**: Secure login system with user and admin roles

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js

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

3. Set up environment variables:
Create a `.env` file in the root directory and add:
```
MONGODB_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Demo Credentials

- **Regular User**:
  - Username: user
  - Password: user

- **Admin**:
  - Username: admin
  - Password: admin

## Project Structure

```
IngredientAI/
├── app.py              # Main Flask application
├── db_config.py        # Database configuration
├── ingredient_analyzer.py  # Core analysis logic
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript files
└── templates/         # HTML templates
    ├── login.html
    └── dashboard.html
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
