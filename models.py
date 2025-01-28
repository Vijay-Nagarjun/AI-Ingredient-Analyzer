import datetime
import bcrypt
from bson import ObjectId

class User:
    def __init__(self, db):
        self.collection = db.users

    def create_user(self, username, email, password):
        # Check if user already exists
        if self.collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            raise ValueError("Username or email already exists")

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow(),
            "is_active": True
        }
        
        result = self.collection.insert_one(user_doc)
        return str(result.inserted_id)

    def verify_user(self, username, password):
        user = self.collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return user
        return None

class Admin:
    def __init__(self, db):
        self.collection = db.admins

    def create_admin(self, username, email, password):
        # Check if admin already exists
        if self.collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            raise ValueError("Admin username or email already exists")

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        admin_doc = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow(),
            "is_active": True
        }
        
        result = self.collection.insert_one(admin_doc)
        return str(result.inserted_id)

    def verify_admin(self, username, password):
        admin = self.collection.find_one({"username": username})
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password']):
            return admin
        return None

class IngredientAnalysis:
    def __init__(self, db):
        self.collection = db.ingredient_analyses

    def save_analysis(self, user_id, ingredients_text, analysis_result):
        """
        Save an ingredient analysis result to the database
        
        Parameters:
        - user_id: ObjectId or str of the user who performed the analysis
        - ingredients_text: Original ingredients text that was analyzed
        - analysis_result: Dictionary containing the analysis results
        """
        analysis_doc = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "ingredients_text": ingredients_text,
            "ingredients": analysis_result.get("ingredients", []),
            "ingredient_percentages": analysis_result.get("ingredient_percentages", {}),
            "health_score": analysis_result.get("health_score", 0),
            "product_name": analysis_result.get("product_name", "Unnamed Product"),
            "created_at": datetime.datetime.utcnow()
        }
        
        result = self.collection.insert_one(analysis_doc)
        return str(result.inserted_id)

    def get_user_analyses(self, user_id, skip=0, limit=10):
        """
        Get all analyses for a specific user, with pagination
        
        Parameters:
        - user_id: ObjectId or str of the user
        - skip: Number of results to skip (for pagination)
        - limit: Maximum number of results to return
        """
        user_id_obj = ObjectId(user_id) if isinstance(user_id, str) else user_id
        cursor = self.collection.find(
            {"user_id": user_id_obj}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        return list(cursor)

    def get_analysis_by_id(self, analysis_id):
        """
        Get a specific analysis by its ID
        
        Parameters:
        - analysis_id: ObjectId or str of the analysis
        """
        analysis_id_obj = ObjectId(analysis_id) if isinstance(analysis_id, str) else analysis_id
        return self.collection.find_one({"_id": analysis_id_obj})

    def get_user_analysis_stats(self, user_id):
        """
        Get statistics about a user's analyses
        
        Parameters:
        - user_id: ObjectId or str of the user
        """
        user_id_obj = ObjectId(user_id) if isinstance(user_id, str) else user_id
        pipeline = [
            {"$match": {"user_id": user_id_obj}},
            {"$group": {
                "_id": None,
                "total_analyses": {"$sum": 1},
                "avg_health_score": {"$avg": "$health_score"},
                "category_counts": {
                    "$push": "$ingredient_percentages"
                }
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "total_analyses": 0,
                "avg_health_score": 0,
                "category_averages": {}
            }
            
        stats = result[0]
        
        # Calculate average percentages for each category
        category_counts = stats["category_counts"]
        category_averages = {}
        
        if category_counts:
            categories = category_counts[0].keys()
            for category in categories:
                total = sum(count.get(category, 0) for count in category_counts)
                category_averages[category] = round(total / len(category_counts), 2)
        
        return {
            "total_analyses": stats["total_analyses"],
            "avg_health_score": round(stats["avg_health_score"], 2),
            "category_averages": category_averages
        }

    def delete_analysis(self, analysis_id):
        """
        Delete a specific analysis
        
        Parameters:
        - analysis_id: ObjectId or str of the analysis to delete
        """
        analysis_id_obj = ObjectId(analysis_id) if isinstance(analysis_id, str) else analysis_id
        result = self.collection.delete_one({"_id": analysis_id_obj})
        return result.deleted_count > 0