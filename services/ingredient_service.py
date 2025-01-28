import os
import json
import requests
from dotenv import load_dotenv
import logging
from functools import lru_cache
from openai import OpenAI
import re

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class IngredientService:
    def __init__(self):
        self.categories = ["Natural", "Additives", "Preservatives", "Artificial Colors", "Highly Processed"]
        self.category_colors = {
            "Natural": "#4CAF50",  # Green
            "Additives": "#FFC107",  # Amber
            "Preservatives": "#FF9800",  # Orange
            "Artificial Colors": "#F44336",  # Red
            "Highly Processed": "#9C27B0"  # Purple
        }
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found")

    @lru_cache(maxsize=100)
    def analyze_ingredients(self, ingredients_text):
        """Analyze ingredients using OpenAI API."""
        try:
            # Clean and validate input text
            if not ingredients_text or len(ingredients_text.strip()) < 3:
                raise ValueError("No valid ingredients text provided")

            # Prepare the prompt for OpenAI
            messages = [
                {"role": "system", "content": """You are an expert in analyzing food ingredients. Analyze the given ingredients list and:
1. Categorize ingredients into: Natural, Additives, Preservatives, Artificial Colors, Highly Processed
2. Calculate percentage distribution of these categories
3. Calculate a health score (0-100)
4. Return the analysis in this exact JSON format:
{
    "health_score": <score>,
    "ingredients": [{"name": "<ingredient>", "category": "<category>"}],
    "ingredient_percentages": {
        "Natural": <percentage>,
        "Additives": <percentage>,
        "Preservatives": <percentage>,
        "Artificial Colors": <percentage>,
        "Highly Processed": <percentage>
    }
}"""},
                {"role": "user", "content": f"Analyze these ingredients: {ingredients_text}"}
            ]

            try:
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.3
                )
                
                # Parse response
                result = response.choices[0].message.content
                return json.loads(result)
                
            except Exception as e:
                error_msg = str(e)
                if "insufficient_quota" in error_msg or "exceeded your current quota" in error_msg:
                    logger.error("OpenAI API quota exceeded. Please check your billing status.")
                    raise ValueError(
                        "OpenAI API quota exceeded. Please check your OpenAI account billing status at "
                        "https://platform.openai.com/account/billing/overview"
                    )
                else:
                    logger.error(f"Error in OpenAI API call: {error_msg}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error in analyze_ingredients: {str(e)}")
            raise
