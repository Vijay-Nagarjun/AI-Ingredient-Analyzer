import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            # Get MongoDB URI from environment variable
            mongodb_uri = os.getenv('MONGODB_URI')
            if not mongodb_uri:
                raise ValueError("MongoDB URI not found in environment variables")

            # Create MongoDB client
            self.client = MongoClient(mongodb_uri)
            
            # Access the database
            self.db = self.client.get_database()
            
            # Test the connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise

    def get_db(self):
        return self.db

    def close(self):
        if self.client:
            self.client.close()