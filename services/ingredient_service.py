import os
import json
import requests
from dotenv import load_dotenv
import logging
from functools import lru_cache

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
        
    def normalize_percentages(self, percentages):
        """Normalize percentages to ensure they sum to 100%."""
        total = sum(percentages.values())
        if total == 0:
            # If all percentages are 0, distribute evenly
            return {k: 20 for k in self.categories}
        return {k: round((v / total) * 100, 1) for k, v in percentages.items()}

    @lru_cache(maxsize=100)
    def analyze_ingredients(self, ingredients_text):
        """Analyze ingredients using Deepseek LLM via Ollama."""
        try:
            # Clean and validate input text
            if not ingredients_text or len(ingredients_text.strip()) < 3:
                raise ValueError("No valid ingredients text provided")

            # Prepare the prompt
            prompt = f"""You are an expert in analyzing food ingredients. Analyze these ingredients: {ingredients_text}

Return the analysis in this exact JSON format:
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
}}

Categories should be one of: Natural, Additives, Preservatives, Artificial Colors, Highly Processed.
Health score should be between 0-100.
Make sure the percentages sum to 100%."""

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
                # Extract JSON from the response text
                json_str = result[result.find("{"):result.rfind("}")+1]
                analysis = json.loads(json_str)
                
                # Normalize percentages
                analysis['ingredient_percentages'] = self.normalize_percentages(analysis['ingredient_percentages'])
                
                return analysis
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling Ollama API: {str(e)}")
                raise ValueError("Failed to connect to Ollama. Make sure Ollama is running and Deepseek model is installed.")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response: {str(e)}")
                raise ValueError("Failed to parse the LLM response. The model might have returned an invalid format.")
                    
        except Exception as e:
            logger.error(f"Error in analyze_ingredients: {str(e)}")
            raise