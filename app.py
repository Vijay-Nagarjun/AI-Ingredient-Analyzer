from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
import base64
from io import BytesIO
from PIL import Image, ImageEnhance
import pytesseract
import json
from models import User, Admin, IngredientAnalysis
from bson import ObjectId
from datetime import datetime, timedelta
import tempfile
import random
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# MongoDB setup
try:
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ingredient_analyzer']
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection error: {str(e)}")
    db = None

# Initialize database
user_model = User(db)
admin_model = Admin(db)
analysis_model = IngredientAnalysis(db)

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            print("Login attempt received")
            
            # Check request content type
            print("Content-Type:", request.content_type)
            
            # Try to get JSON data
            try:
                data = request.get_json()
                print("Received data:", data)
            except Exception as e:
                print("Error parsing JSON:", str(e))
                return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
            
            if not data:
                print("No JSON data received")
                return jsonify({'success': False, 'message': 'No data provided'}), 400
                
            username = data.get('username')
            password = data.get('password')
            
            print(f"Login attempt - Username: {username}")
            
            if not username or not password:
                print("Missing username or password")
                return jsonify({'success': False, 'message': 'Username and password are required'}), 400

            # Try regular user login first
            try:
                user = user_model.verify_user(username, password)
                if user:
                    session['user_id'] = str(user['_id'])
                    session['is_admin'] = False
                    print(f"User login successful: {username}")
                    return jsonify({'success': True, 'is_admin': False})
            except Exception as e:
                print(f"Error during user verification: {str(e)}")

            # Try admin login
            try:
                admin = admin_model.verify_admin(username, password)
                if admin:
                    session['user_id'] = str(admin['_id'])
                    session['is_admin'] = True
                    print(f"Admin login successful: {username}")
                    return jsonify({'success': True, 'is_admin': True})
            except Exception as e:
                print(f"Error during admin verification: {str(e)}")

            print(f"Login failed for user: {username}")
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    
    try:
        # Get user analyses
        if is_admin:
            # For admin, get all analyses
            analyses = []
            users = list(user_model.collection.find())
            for user in users:
                user_analyses = analysis_model.get_user_analyses(str(user['_id']))
                for analysis in user_analyses:
                    if analysis:
                        serialized = serialize_analysis(analysis)
                        if serialized:
                            serialized['username'] = user.get('username', 'Unknown')
                            analyses.append(serialized)
        else:
            # For regular users, get only their analyses
            user_analyses = analysis_model.get_user_analyses(user_id)
            analyses = []
            for analysis in user_analyses:
                if analysis:
                    serialized = serialize_analysis(analysis)
                    if serialized:
                        analyses.append(serialized)
        
        # Sort analyses by creation date
        analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Store in session for use in compare view
        session['analysis_history'] = analyses
        
        return render_template('dashboard.html', 
                             analyses=analyses,
                             is_admin=is_admin,
                             analysis_history=analyses)
                             
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        flash("Error loading dashboard data", "error")
        return render_template('dashboard.html', 
                             analyses=[],
                             is_admin=is_admin,
                             analysis_history=[])

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'GET':
        return render_template('analyze.html')
    
    try:
        data = request.get_json()
        if not data or 'type' not in data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data'})
        
        extracted_text = ''
        if data['type'] == 'image':
            try:
                # Remove header of base64 image
                image_data = data['content'].split(',')[1]
                image_bytes = base64.b64decode(image_data)
                
                # Save image temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(image_bytes)
                    temp_path = temp_file.name

                try:
                    # Use the enhanced OCR from test_ocr.py
                    from tests.test_ocr import extract_text
                    extracted_text = extract_text(temp_path)
                    os.unlink(temp_path)
                except Exception as e:
                    os.unlink(temp_path)
                    return jsonify({'success': False, 'error': f'OCR failed: {str(e)}'})
                
            except Exception as e:
                return jsonify({'success': False, 'error': f'Image processing failed: {str(e)}'})
        else:
            extracted_text = data['content']
        
        if not extracted_text:
            return jsonify({'success': False, 'error': 'No text could be extracted'})

        # Use the ingredient analyzer
        try:
            from Vingredient_analyzer import IngredientAnalyzer
            analyzer = IngredientAnalyzer()
            analysis_result = analyzer.analyze_ingredients(extracted_text)
            
            # Add the extracted text to the result
            analysis_result['extracted_text'] = extracted_text
            analysis_result['success'] = True
            
            # Store in database
            user_id = session.get('user_id')
            if user_id:
                analysis_model.save_analysis(
                    user_id=user_id,
                    ingredients_text=extracted_text,
                    analysis_result=analysis_result
                )
            
            return jsonify(analysis_result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'})
        
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/history')
@login_required
def history():
    try:
        user_id = session.get('user_id')
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Get paginated analyses from database
        analyses = list(analysis_model.get_user_analyses(
            user_id=user_id,
            skip=(page - 1) * per_page,
            limit=per_page
        ))
        
        # Process analyses for display
        processed_analyses = []
        for analysis in analyses:
            # First serialize MongoDB objects
            analysis = serialize_mongo_doc(analysis)
            
            # Format created_at date
            if 'created_at' in analysis:
                created_at = analysis['created_at']
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S')
                        except:
                            created_at = datetime.now()
                analysis['created_at'] = created_at.strftime('%B %d, %Y %I:%M %p')
            
            # Ensure we have ingredient percentages
            if 'ingredient_percentages' not in analysis:
                analysis['ingredient_percentages'] = {
                    'Natural': 0,
                    'Additives': 0,
                    'Preservatives': 0,
                    'Artificial Colors': 0,
                    'Highly Processed': 0
                }
            
            if 'health_score' not in analysis:
                analysis['health_score'] = calculate_health_score(analysis['ingredient_percentages'])
            
            if 'ingredients_text' not in analysis:
                analysis['ingredients_text'] = 'No ingredients listed'
                
            if 'product_name' not in analysis:
                analysis['product_name'] = 'Unnamed Product'
                
            processed_analyses.append(analysis)
        
        # Sort by created_at date
        processed_analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return render_template('history_new.html', 
                             analyses=processed_analyses,
                             page=page,
                             has_next=len(analyses) == per_page)
                             
    except Exception as e:
        print(f"Error loading history: {str(e)}")
        flash(f"Error loading history: {str(e)}", 'error')
        return redirect(url_for('dashboard'))

@app.route('/analyze_with_ai', methods=['POST'])
@login_required
def analyze_with_ai():
    data = request.get_json()
    ingredients_text = data.get('text', '').strip()
    
    if not ingredients_text:
        return jsonify({
            'success': False,
            'error': "No ingredients text provided"
        }), 400
            
    # Here we'll add OpenAI integration later
    # For now, just use our basic analyzer
    analyzer = IngredientAnalyzer()
    result = analyzer.analyze_ingredients(ingredients_text)
    print("Analysis result:", result)  # Debug log
    
    if 'error' in result:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 400
            
    return jsonify({
        'success': True,
        'result': result
    })

@app.route('/compare')
@login_required
def compare_page():
    user_id = session.get('user_id')
    analyses = list(analysis_model.get_user_analyses(user_id))
    
    # Process analyses for display
    for analysis in analyses:
        analysis['_id'] = str(analysis['_id'])
        analysis['date'] = analysis['created_at'].strftime('%Y-%m-%d %H:%M')
        
        if 'ingredient_categories' not in analysis:
            analysis['ingredient_categories'] = {
                'Natural': 45,
                'Additives': 20,
                'Preservatives': 15,
                'Colors': 10,
                'Others': 10
            }
            
        if 'health_score' not in analysis:
            analysis['health_score'] = 75
            
        if 'product_name' not in analysis:
            analysis['product_name'] = 'Unnamed Product'
            
        if 'ingredients_text' not in analysis:
            analysis['ingredients_text'] = 'No ingredients listed'
    
    return render_template('compare.html', analyses=analyses)

@app.route('/compare_analyses', methods=['POST'])
@login_required
def compare_analyses():
    try:
        data = request.get_json()
        analysis_ids = data.get('analysis_ids', [])
        
        if not analysis_ids:
            return jsonify({'success': False, 'message': 'No analyses selected'})
        
        if len(analysis_ids) < 2:
            return jsonify({'success': False, 'message': 'Please select at least 2 products to compare'})
        
        analyses = []
        for analysis_id in analysis_ids:
            analysis = analysis_model.get_analysis_by_id(analysis_id)
            if analysis:
                # First serialize MongoDB objects
                analysis = serialize_mongo_doc(analysis)
                
                # Ensure we have ingredient percentages
                if 'ingredient_percentages' not in analysis:
                    analysis['ingredient_percentages'] = {
                        'Natural': 0,
                        'Additives': 0,
                        'Preservatives': 0,
                        'Artificial Colors': 0,
                        'Highly Processed': 0
                    }
                
                # For backward compatibility with UI
                analysis['ingredient_categories'] = analysis['ingredient_percentages']
                
                if 'health_score' not in analysis:
                    analysis['health_score'] = calculate_health_score(analysis['ingredient_percentages'])
                    
                if 'product_name' not in analysis:
                    analysis['product_name'] = 'Unnamed Product'
                    
                if 'ingredients_text' not in analysis:
                    analysis['ingredients_text'] = 'No ingredients listed'
                
                analyses.append(analysis)
        
        return jsonify({
            'success': True,
            'analyses': analyses
        })
        
    except Exception as e:
        print(f"Error in compare_analyses: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred while comparing analyses: {str(e)}'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    
    try:
        # Get all users
        users = list(user_model.collection.find())
        
        # Get analyses for each user
        for user in users:
            # Get raw analyses
            analyses = list(analysis_model.collection.find({"user_id": str(user['_id'])}).sort("created_at", -1))
            
            # Serialize each analysis
            serialized_analyses = []
            for analysis in analyses:
                serialized = serialize_analysis(analysis)
                if serialized:
                    serialized_analyses.append(serialized)
            
            # Add to user object
            user['analyses'] = serialized_analyses
            user['analysis_count'] = len(serialized_analyses)
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
        
        return render_template('admin.html', users=users)
        
    except Exception as e:
        print(f"Admin page error: {str(e)}")
        flash("Error loading admin data", "error")
        return render_template('admin.html', users=[])

@app.route('/admin/user/<user_id>/analyses')
@login_required
def user_analyses(user_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = user_model.collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    analyses = list(analysis_model.collection.find({"user_id": user_id}).sort("created_at", -1))
    return render_template('user_analyses.html', analyses=analyses, user=user)

@app.route('/api/admin/stats')
@login_required
def admin_stats():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get stats from database
    try:
        # Placeholder data - replace with actual database queries
        stats = {
            'totalUsers': 10,
            'totalAnalyses': 50,
            'activeToday': 5
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/activity')
@login_required
def admin_activity():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get activity log from database
    try:
        # Placeholder data - replace with actual database queries
        activities = [
            {
                'timestamp': '2024-12-25T10:30:00',
                'username': 'user1',
                'action': 'Analysis',
                'details': 'Analyzed product ingredients'
            }
        ]
        return jsonify({'activities': activities})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users')
@login_required
def admin_users():
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user list from database
    try:
        # Placeholder data - replace with actual database queries
        users = [
            {
                '_id': '1',
                'username': 'user1',
                'email': 'user1@example.com',
                'lastActive': '2024-12-25T10:30:00',
                'active': True
            }
        ]
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Delete user from database
    try:
        # Placeholder - replace with actual database operation
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_ingredients(text):
    """Extract ingredients from text using simple rules."""
    # Remove common words and clean text
    text = text.lower()
    text = re.sub(r'ingredients:', '', text)
    text = re.sub(r'[^\w\s,]', '', text)
    
    # Split by commas or spaces
    ingredients = [ing.strip() for ing in re.split(r'[,\n]', text)]
    
    # Filter out empty strings and common words
    ingredients = [ing for ing in ingredients if ing and len(ing) > 1]
    
    # Return unique ingredients
    return list(set(ingredients))

def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if isinstance(doc, dict):
        return {k: serialize_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return doc

def serialize_analysis(analysis):
    if not analysis:
        return None
    
    try:
        # Convert ObjectId to string
        analysis['_id'] = str(analysis['_id'])
        analysis['user_id'] = str(analysis['user_id'])
        
        # Convert datetime to string
        if 'created_at' in analysis:
            analysis['created_at'] = analysis['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
        # Handle undefined values in analysis_result
        if 'analysis_result' in analysis:
            result = analysis['analysis_result']
            if isinstance(result, dict):
                if 'ingredients' in result:
                    result['ingredients'] = [i for i in result['ingredients'] if i is not None]
                if 'health_score' not in result:
                    result['health_score'] = 0
                    
        return analysis
    except Exception as e:
        print(f"Error serializing analysis: {str(e)}")
        return None

def calculate_health_score(percentages):
    """Calculate health score based on ingredient percentages"""
    weights = {
        'Natural': 1.0,
        'Additives': -0.3,
        'Preservatives': -0.3,
        'Artificial Colors': -0.2,
        'Highly Processed': -0.4
    }
    
    score = sum(percentages[cat] * weights[cat] for cat in percentages)
    # Normalize to 0-100 range
    normalized_score = min(max(50 + score/2, 0), 100)
    return round(normalized_score, 1)

if __name__ == '__main__':
    # Check MongoDB connection and list users
    try:
        print("Checking MongoDB connection...")
        # List all users
        users = list(user_model.collection.find({}, {"username": 1, "_id": 0}))
        print("Existing users:", [user['username'] for user in users])
        
        # Check if user1 exists, if not create it
        user1 = user_model.collection.find_one({"username": "user1"})
        if not user1:
            print("Creating user1...")
            user_model.create_user("user1", "user1@example.com", "1")
            print("Created user1 - username: user1, password: 1")
        else:
            print("user1 already exists")
            
    except Exception as e:
        print(f"MongoDB Error: {str(e)}")
        
    app.run(host='0.0.0.0', port=5000, debug=True)
