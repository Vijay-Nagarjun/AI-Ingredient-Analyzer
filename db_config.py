import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    def __init__(self):
        # Connect to local MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['ingredient_analyzer']

    def get_db(self):
        return self.db

    def close(self):
        if self.client:
            self.client.close()