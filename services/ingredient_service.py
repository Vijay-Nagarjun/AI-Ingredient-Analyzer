import os
import json
import requests
from dotenv import load_dotenv
import logging
from functools import lru_cache
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
        self.ollama_url = "http://localhost:11434/api/generate"

    @lru_cache(maxsize=100)
    def analyze_ingredients(self, ingredients_text):
        """Analyze ingredients using Deepseek-LLM via Ollama."""
        try:
            # Clean and validate input text
            if not ingredients_text or len(ingredients_text.strip()) < 3:
                raise ValueError("No valid ingredients text provided")

            # Prepare the prompt
            prompt = f"""You are an expert in analyzing food ingredients. Analyze these ingredients: {ingredients_text}

Please analyze the ingredients and:
1. Categorize ingredients into: Natural, Additives, Preservatives, Artificial Colors, Highly Processed
2. Calculate percentage distribution of these categories
3. Calculate a health score (0-100)
4. Return the analysis in this exact JSON format:
{{
    "health_score": <score>,
    "ingredients": [{{"name": "<ingredient>", "category": "<category>"}}],
    "ingredient_percentages": {{
        "Natural": <percentage>,
        "Additives": <percentage>,
        "Preservatives": <percentage>,
        "Artificial Colors": <percentage>,
        "Highly Processed": <percentage>
    }}
}}"""

            try:
                # Call Ollama API
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": "deepseek-llm",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                
                # Parse response
                result = response.json()["response"]
                # Extract JSON from the response (it might be wrapped in markdown code blocks)
                json_match = re.search(r'({.*})', result, re.DOTALL)
                if json_match:
                    result = json_match.group(1)
                return json.loads(result)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling Ollama API: {str(e)}")
                raise ValueError("Failed to connect to Ollama. Make sure Ollama is running with deepseek-llm model.")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Ollama response: {str(e)}")
                raise ValueError("Invalid response format from Ollama")
                    
        except Exception as e:
            logger.error(f"Error in analyze_ingredients: {str(e)}")
            raise
