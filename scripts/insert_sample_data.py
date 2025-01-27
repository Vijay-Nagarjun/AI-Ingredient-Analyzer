from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import os
import sys
import random

# Add parent directory to path to import from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import IngredientAnalysis
from db_config import DatabaseConfig

# Sample ingredient data
SAMPLE_ANALYSES = [
    {
        "ingredients_text": "Water, Sugar, Wheat Flour, Palm Oil, Cocoa Powder (2%), Salt, Emulsifier (E442, E476), Natural Vanilla Flavoring",
        "product_name": "Chocolate Cookie",
        "category_data": {
            "Natural": ["Water", "Sugar", "Wheat Flour", "Cocoa Powder", "Salt", "Natural Vanilla Flavoring"],
            "Additives": ["E442", "E476"],
            "Preservatives": [],
            "Artificial Colors": [],
            "Highly Processed": ["Palm Oil"]
        }
    },
    {
        "ingredients_text": "Carbonated Water, High Fructose Corn Syrup, Caramel Color (E150d), Phosphoric Acid, Natural Flavors, Caffeine",
        "product_name": "Cola Drink",
        "category_data": {
            "Natural": ["Carbonated Water", "Natural Flavors"],
            "Additives": ["Phosphoric Acid", "Caffeine"],
            "Preservatives": [],
            "Artificial Colors": ["Caramel Color (E150d)"],
            "Highly Processed": ["High Fructose Corn Syrup"]
        }
    },
    {
        "ingredients_text": "Yogurt (Milk, Live Cultures), Strawberries (15%), Sugar, Modified Corn Starch, Natural Flavors, Carmine (for color)",
        "product_name": "Strawberry Yogurt",
        "category_data": {
            "Natural": ["Milk", "Live Cultures", "Strawberries", "Sugar", "Natural Flavors"],
            "Additives": [],
            "Preservatives": [],
            "Artificial Colors": ["Carmine"],
            "Highly Processed": ["Modified Corn Starch"]
        }
    },
    {
        "ingredients_text": "Chicken, Water, Modified Food Starch, Salt, Sodium Phosphates, Natural Flavoring, Yellow 5, Red 40",
        "product_name": "Chicken Nuggets",
        "category_data": {
            "Natural": ["Chicken", "Water", "Salt", "Natural Flavoring"],
            "Additives": ["Sodium Phosphates"],
            "Preservatives": [],
            "Artificial Colors": ["Yellow 5", "Red 40"],
            "Highly Processed": ["Modified Food Starch"]
        }
    },
    {
        "ingredients_text": "Organic Oats, Organic Brown Sugar, Organic Almonds, Organic Honey, Sea Salt",
        "product_name": "Organic Granola",
        "category_data": {
            "Natural": ["Organic Oats", "Organic Brown Sugar", "Organic Almonds", "Organic Honey", "Sea Salt"],
            "Additives": [],
            "Preservatives": [],
            "Artificial Colors": [],
            "Highly Processed": []
        }
    }
]

def calculate_percentages(category_data):
    total_ingredients = sum(len(ingredients) for ingredients in category_data.values())
    return {
        category: round((len(ingredients) / total_ingredients) * 100, 2)
        for category, ingredients in category_data.items()
    }

def calculate_health_score(percentages):
    weights = {
        'Natural': 1.0,
        'Additives': -0.3,
        'Preservatives': -0.3,
        'Artificial Colors': -0.2,
        'Highly Processed': -0.4
    }
    score = sum(percentages[cat] * weights[cat] for cat in percentages)
    normalized_score = min(max(50 + score/2, 0), 100)
    return round(normalized_score, 1)

def main():
    # Initialize database
    db = DatabaseConfig().get_db()
    analysis_model = IngredientAnalysis(db)
    
    # Get user1's ID (assuming it exists)
    user = db.users.find_one({"username": "user"})
    if not user:
        print("User 'user' not found. Please create a user first.")
        return
    
    user_id = user['_id']
    
    # Create analyses with different timestamps
    base_time = datetime.utcnow() - timedelta(days=7)
    
    for i, sample in enumerate(SAMPLE_ANALYSES):
        # Calculate ingredient percentages
        ingredient_percentages = calculate_percentages(sample['category_data'])
        health_score = calculate_health_score(ingredient_percentages)
        
        # Create ingredients list
        ingredients = []
        for category, items in sample['category_data'].items():
            for item in items:
                ingredients.append({
                    "name": item,
                    "category": category,
                    "percentage": round(100 / sum(len(x) for x in sample['category_data'].values()), 2)
                })
        
        # Create analysis result
        analysis_result = {
            "ingredients": ingredients,
            "classification_summary": sample['category_data'],
            "ingredient_percentages": ingredient_percentages,
            "health_score": health_score,
            "product_name": sample['product_name']
        }
        
        # Insert with timestamp spread over the last week
        doc = {
            "user_id": user_id,
            "ingredients_text": sample['ingredients_text'],
            "ingredients": analysis_result['ingredients'],
            "classification_summary": analysis_result['classification_summary'],
            "ingredient_percentages": analysis_result['ingredient_percentages'],
            "health_score": analysis_result['health_score'],
            "product_name": sample['product_name'],
            "created_at": base_time + timedelta(days=i)
        }
        
        db.ingredient_analyses.insert_one(doc)
        print(f"Inserted analysis for {sample['product_name']}")

if __name__ == "__main__":
    main()
