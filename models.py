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
        analysis_doc = {
            "user_id": user_id,
            "ingredients_text": ingredients_text,
            "analysis_result": analysis_result,
            "created_at": datetime.datetime.utcnow()
        }
        
        result = self.collection.insert_one(analysis_doc)
        return str(result.inserted_id)

    def get_user_analyses(self, user_id):
        return list(self.collection.find({"user_id": user_id}).sort("created_at", -1))

    def get_analysis_by_id(self, analysis_id):
        return self.collection.find_one({"_id": ObjectId(analysis_id)})