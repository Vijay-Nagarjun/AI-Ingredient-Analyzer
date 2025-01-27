from datetime import datetime
import bcrypt
import os
import sys

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import DatabaseConfig
from models import User, Admin, IngredientAnalysis

def create_dummy_data():
    print("Starting dummy data creation...")
    db_config = DatabaseConfig()
    db = db_config.get_db()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.users.delete_many({})
        db.admins.delete_many({})
        db.ingredient_analyses.delete_many({})
        
        # Create dummy user
        print("Creating dummy user...")
        hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
        dummy_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': hashed_password,
            'created_at': datetime.now()
        }
        user_result = db.users.insert_one(dummy_user)
        
        # Create dummy admin
        print("Creating dummy admin...")
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        dummy_admin = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': admin_password,
            'created_at': datetime.now()
        }
        db.admins.insert_one(dummy_admin)
        
        # Create dummy analyses
        print("Creating dummy analyses...")
        dummy_analyses = [
            {
                'user_id': user_result.inserted_id,
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
                'user_id': user_result.inserted_id,
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
        
        # Print login credentials
        print("\nLogin Credentials:")
        print("Regular User:")
        print("Username: testuser")
        print("Password: password123")
        print("\nAdmin User:")
        print("Username: admin")
        print("Password: admin123")
        
    except Exception as e:
        print(f"Error creating dummy data: {str(e)}")
    finally:
        db_config.close()

if __name__ == '__main__':
    create_dummy_data()
