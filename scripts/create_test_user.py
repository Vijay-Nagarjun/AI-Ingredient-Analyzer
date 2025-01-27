import sys
import os

# Add parent directory to path to import from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import User
from db_config import DatabaseConfig

def main():
    # Initialize database
    db = DatabaseConfig().get_db()
    user_model = User(db)
    
    try:
        # Create test user
        user_id = user_model.create_user(
            username="user",
            email="user@example.com",
            password="user123"
        )
        print(f"Created test user with ID: {user_id}")
        print("Username: user")
        print("Password: user123")
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
