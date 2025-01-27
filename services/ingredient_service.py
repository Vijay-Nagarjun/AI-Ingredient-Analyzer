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
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found")
        
        # Set up the system instruction
        self.system_instruction = """Analyze ingredients and calculate their percentages based on available information. Follow these rules:

1. If nutritional information is provided:
   - Use Total Fat content for oil/fat-based ingredients
   - Use Protein content for protein-rich ingredients
   - Use Carbohydrate content for starch/sugar-based ingredients
   - Use Sodium content for salt and seasoning levels

2. If NO nutritional information is provided:
   - Calculate percentages based on ingredient order (ingredients are listed in descending order by weight)
   - First ingredient should have the highest percentage (typically 30-50%)
   - Second ingredient should have the next highest percentage (typically 15-30%)
   - Following ingredients should have decreasing percentages
   - Minor ingredients (flavors, preservatives, etc.) should have very small percentages (0.1-2%)
   - Ensure all percentages sum to 100%

3. For sub-ingredients in parentheses:
   - Distribute their percentages within their parent ingredient's percentage
   - Example: "Seasoning (Salt, Spices)" - calculate sub-percentages within the Seasoning's total percentage

Format response as:
{
  "ingredients": [{"name": "string", "category": "string", "percentage": "number"}],
  "classification_summary": {"Natural": [], "Additives": [], "Preservatives": [], "Artificial Colors": [], "Highly Processed": []},
  "ingredient_percentages": {"Natural": 0-100, "Additives": 0-100, "Preservatives": 0-100, "Artificial Colors": 0-100, "Highly Processed": 0-100}
}

Return ONLY valid JSON."""

    @lru_cache(maxsize=100)
    def analyze_ingredients(self, ingredients_text, nutritional_info=None):
        """
        Analyze ingredients using OpenAI API
        Uses caching to prevent duplicate API calls
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the message
            user_message = f"Analyze these ingredients:\n{ingredients_text}"
            if nutritional_info:
                user_message += f"\n\nNutritional Information:\n{nutritional_info}"
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            # Make the API call
            response = requests.post(self.openai_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            if not result.get('choices'):
                raise ValueError("No response choices found")
            
            # Extract and parse the analysis
            analysis_text = result['choices'][0]['message']['content']
            analysis = json.loads(analysis_text)
            
            # Calculate health score
            health_score = self.calculate_health_score(analysis['ingredient_percentages'])
            analysis['health_score'] = health_score
            analysis['success'] = True
            
            return analysis
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to connect to analysis service'
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            return {
                'success': False,
                'error': 'Invalid response from analysis service'
            }
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def calculate_health_score(self, percentages):
        """Calculate health score based on ingredient percentages"""
        weights = {
            'Natural': 1.0,
            'Additives': -0.3,
            'Preservatives': -0.3,
            'Artificial Colors': -0.2,
            'Highly Processed': -0.4
        }
        
        score = sum(percentages[cat] * weights[cat] for cat in percentages)
        # Normalize to 0-100 range
        normalized_score = min(max(50 + score/2, 0), 100)
        return round(normalized_score, 1)
