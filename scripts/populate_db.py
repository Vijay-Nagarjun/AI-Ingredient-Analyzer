import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_config import DatabaseConfig
from models import User, Admin, IngredientAnalysis
import datetime
import random
from bson import ObjectId

# Sample food products with ingredients
SAMPLE_PRODUCTS = [
    {
        "name": "Organic Granola",
        "ingredients": "Rolled Oats, Honey, Almonds, Coconut Oil, Pumpkin Seeds, Chia Seeds, Cinnamon",
        "analysis": {
            "natural": ["Rolled Oats", "Honey", "Almonds", "Pumpkin Seeds", "Chia Seeds", "Cinnamon"],
            "additives": [],
            "preservatives": [],
            "artificial_colors": [],
            "highly_processed": ["Coconut Oil"],
            "health_score": 4.5,
            "processing_level": 1.5,
            "nutrient_density": 4.8
        }
    },
    {
        "name": "Greek Yogurt",
        "ingredients": "Pasteurized Milk, Live Active Cultures (S. Thermophilus, L. Bulgaricus, L. Acidophilus, Bifidus, L. Casei)",
        "analysis": {
            "natural": ["Milk", "Live Active Cultures"],
            "additives": [],
            "preservatives": [],
            "artificial_colors": [],
            "highly_processed": [],
            "health_score": 4.8,
            "processing_level": 2.0,
            "nutrient_density": 4.5
        }
    },
    {
        "name": "Veggie Chips",
        "ingredients": "Root Vegetables (Sweet Potatoes, Carrots, Taro, Batata, Parsnip), Canola Oil and/or Safflower Oil and/or Sunflower Oil, Sea Salt",
        "analysis": {
            "natural": ["Sweet Potatoes", "Carrots", "Taro", "Batata", "Parsnip"],
            "additives": [],
            "preservatives": [],
            "artificial_colors": [],
            "highly_processed": ["Canola Oil", "Safflower Oil", "Sunflower Oil"],
            "health_score": 3.8,
            "processing_level": 3.0,
            "nutrient_density": 3.5
        }
    },
    {
        "name": "Protein Bar",
        "ingredients": "Protein Blend (Whey Protein Isolate, Milk Protein Isolate), Soluble Corn Fiber, Almonds, Water, Erythritol, Natural Flavors, Sea Salt, Sucralose",
        "analysis": {
            "natural": ["Almonds"],
            "additives": ["Natural Flavors", "Sucralose"],
            "preservatives": [],
            "artificial_colors": [],
            "highly_processed": ["Whey Protein Isolate", "Milk Protein Isolate", "Soluble Corn Fiber", "Erythritol"],
            "health_score": 3.2,
            "processing_level": 4.0,
            "nutrient_density": 3.8
        }
    },
    {
        "name": "Fruit Smoothie",
        "ingredients": "Apple Juice, Strawberries, Bananas, Greek Yogurt, Honey, Chia Seeds",
        "analysis": {
            "natural": ["Apple Juice", "Strawberries", "Bananas", "Greek Yogurt", "Honey", "Chia Seeds"],
            "additives": [],
            "preservatives": [],
            "artificial_colors": [],
            "highly_processed": [],
            "health_score": 4.6,
            "processing_level": 1.0,
            "nutrient_density": 4.2
        }
    }
]

def create_or_get_users(user_model):
    users = [
        {"username": "user1", "email": "user1@example.com", "password": "password1"},
        {"username": "user2", "email": "user2@example.com", "password": "password2"},
        {"username": "user3", "email": "user3@example.com", "password": "password3"}
    ]
    
    user_ids = []
    for user in users:
        # Try to find existing user
        existing_user = user_model.collection.find_one({"username": user["username"]})
        if existing_user:
            user_ids.append(str(existing_user["_id"]))
            print(f"Using existing user: {user['username']}")
        else:
            try:
                user_id = user_model.create_user(user["username"], user["email"], user["password"])
                user_ids.append(user_id)
                print(f"Created new user: {user['username']}")
            except ValueError as e:
                print(f"Error creating {user['username']}: {str(e)}")
    
    return user_ids

def create_or_get_admin(admin_model):
    # Try to find existing admin
    existing_admin = admin_model.collection.find_one({"username": "admin"})
    if existing_admin:
        print("Using existing admin user")
        return str(existing_admin["_id"])
    
    try:
        admin_id = admin_model.create_admin("admin", "admin@example.com", "adminpass123")
        print("Created new admin user")
        return admin_id
    except ValueError as e:
        print(f"Error creating admin: {str(e)}")
        return None

def create_analyses(analysis_model, user_ids):
    # Clear existing analyses
    analysis_model.collection.delete_many({})
    
    for user_id in user_ids:
        # Create multiple analyses for each user
        for _ in range(random.randint(3, 6)):
            product = random.choice(SAMPLE_PRODUCTS)
            
            # Create analysis document with correct structure
            analysis_doc = {
                "user_id": user_id,
                "product_name": product["name"],
                "ingredients_text": product["ingredients"],
                "analysis_result": {
                    "natural": product["analysis"]["natural"],
                    "additives": product["analysis"]["additives"],
                    "preservatives": product["analysis"]["preservatives"],
                    "artificial_colors": product["analysis"]["artificial_colors"],
                    "highly_processed": product["analysis"]["highly_processed"],
                    "health_score": product["analysis"]["health_score"],
                    "processing_level": product["analysis"]["processing_level"],
                    "nutrient_density": product["analysis"]["nutrient_density"]
                },
                "created_at": datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))
            }
            
            # Save to database
            result = analysis_model.collection.insert_one(analysis_doc)
            print(f"Created analysis for user {user_id}: {product['name']}")

def main():
    # Initialize database connection
    db_config = DatabaseConfig()
    db = db_config.get_db()
    
    # Initialize models
    user_model = User(db)
    admin_model = Admin(db)
    analysis_model = IngredientAnalysis(db)
    
    # Create or get users and admin
    user_ids = create_or_get_users(user_model)
    admin_id = create_or_get_admin(admin_model)
    
    # Create analyses for users
    if user_ids:
        create_analyses(analysis_model, user_ids)
    
    print("\nDatabase populated successfully!")
    print("\nTest Credentials:")
    print("Regular Users:")
    print("Username: user1, Password: password1")
    print("Username: user2, Password: password2")
    print("Username: user3, Password: password3")
    print("\nAdmin User:")
    print("Username: admin, Password: adminpass123")

if __name__ == "__main__":
    main()
