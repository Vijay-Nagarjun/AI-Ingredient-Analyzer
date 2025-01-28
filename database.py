from datetime import datetime
import bcrypt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class Database:
    def __init__(self, db_name="ingredient_analyzer"):
        """Initialize database connection"""
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client[db_name]
            self.users = self.db.users
            self.admins = self.db.admins
            
            # Create unique indexes
            self.users.create_index("username", unique=True)
            self.users.create_index("email", unique=True)
            self.admins.create_index("username", unique=True)
            self.admins.create_index("email", unique=True)
            
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    def add_user(self, username, password, email=None, is_admin=False):
        """Add a new user to the database"""
        try:
            # Check if user already exists
            collection = self.admins if is_admin else self.users
            if collection.find_one({"$or": [{"username": username}, {"email": email}]}):
                print(f"{'Admin' if is_admin else 'User'} {username} already exists")
                return False

            # Hash the password using bcrypt
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            user_doc = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            collection.insert_one(user_doc)
            return True
        except Exception as e:
            print(f"Error adding {'admin' if is_admin else 'user'}: {str(e)}")
            return False

def create_sample_users():
    try:
        db = Database()
        
        # First, drop existing collections
        db.users.drop()
        db.admins.drop()
        
        # Sample users with credentials
        regular_users = [
            ("user1", "User1@123", "user1@example.com"),
            ("test_user", "Test@123", "test@example.com")
        ]
        
        admin_users = [
            ("admin", "Admin@123", "admin@example.com")
        ]
        
        print("Creating regular users...")
        for username, password, email in regular_users:
            if db.add_user(username, password, email, is_admin=False):
                print(f"Created user: {username}")
            else:
                print(f"Failed to create user: {username}")
        
        print("\nCreating admin users...")
        for username, password, email in admin_users:
            if db.add_user(username, password, email, is_admin=True):
                print(f"Created admin: {username}")
            else:
                print(f"Failed to create admin: {username}")
        
        print("\nAvailable Users:")
        print("-" * 50)
        print("Regular Users:")
        for username, password, _ in regular_users:
            print(f"Username: {username:<10} Password: {password}")
        
        print("\nAdmin Users:")
        for username, password, _ in admin_users:
            print(f"Username: {username:<10} Password: {password}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error creating sample users: {str(e)}")

if __name__ == "__main__":
    create_sample_users()
