from pymongo import MongoClient
import bcrypt

def check_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ingredient_analyzer
    users = list(db.users.find({}))
    
    print("\nUsers in database:")
    print("-" * 50)
    for user in users:
        print(f"Username: {user.get('username')}")
        print(f"Fields present: {list(user.keys())}")
        print("-" * 50)

    # Test user verification
    test_users = [
        ("user1", "User1@123"),
        ("test_user", "Test@123"),
        ("admin", "Admin@123")
    ]
    
    print("\nTesting user verification:")
    print("-" * 50)
    for username, password in test_users:
        user = db.users.find_one({"username": username})
        if user:
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                    print(f"✓ Password verification successful for {username}")
                else:
                    print(f"✗ Password verification failed for {username}")
            except Exception as e:
                print(f"Error verifying {username}: {str(e)}")
        else:
            print(f"User {username} not found in database")
    print("-" * 50)

if __name__ == "__main__":
    check_database()
