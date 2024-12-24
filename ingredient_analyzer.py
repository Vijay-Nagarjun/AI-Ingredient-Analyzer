import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print the API key (first few characters)
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"API key loaded (first 5 chars): {api_key[:5]}...")
else:
    print("Warning: No API key found in environment variables!")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

class IngredientAnalyzer:
    def __init__(self):
        self.categories = ["Natural", "Additives", "Preservatives", "Artificial Colors", "Highly Processed"]
        
        # Set up the system instruction
        self.system_instruction = """You are an AI specialized in analyzing food ingredients. Your task is to:

1. Classify each ingredient into these categories:
   - Natural: Whole or minimally processed ingredients
   - Additives: Ingredients added for texture, flavor, or preservation
   - Preservatives: Chemicals for shelf life extension
   - Artificial Colors: Synthetic color enhancers
   - Highly Processed: Significantly altered ingredients

2. Score each ingredient on a 1-5 scale for:
   - Processing Level (1=least processed, 5=most processed)
   - Health Impact (1=most healthy, 5=least healthy)
   - Nutrient Density (1=least nutritious, 5=most nutritious)

3. Estimate the percentage of each ingredient based on typical formulations

4. Return the analysis in this exact JSON format:
{
  "ingredients": [
    {
      "name": string,
      "category": string,
      "processing_score": number,
      "health_impact_score": number,
      "nutrient_density_score": number,
      "percentage": number
    }
  ],
  "classification_summary": {
    "Natural": [string],
    "Additives": [string],
    "Preservatives": [string],
    "Artificial Colors": [string],
    "Highly Processed": [string]
  },
  "ingredient_percentages": {
    string: number
  },
  "health_score": number
}

Always return valid JSON that matches this exact format."""
    
    def analyze_ingredients(self, ingredients_text):
        try:
            # Create the chat completion using new API syntax
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": f"Analyze these ingredients: {ingredients_text}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract JSON from response using new API syntax
            json_str = response.choices[0].message.content
            # Parse and validate JSON
            analysis = json.loads(json_str)
            
            # Calculate and update the health score
            if "ingredients" in analysis:
                health_score = self.calculate_health_score(analysis)
                analysis["health_score"] = health_score
                
            return analysis
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def calculate_health_score(self, ingredients_data):
        weights = {
            "processing": 0.5,
            "health_impact": 0.3,
            "nutrient_density": 0.2
        }
        
        total_scores = {"processing": 0, "health_impact": 0, "nutrient_density": 0}
        total_percentage = 0

        for ingredient in ingredients_data["ingredients"]:
            total_scores["processing"] += ingredient["processing_score"] * ingredient["percentage"] / 100
            total_scores["health_impact"] += ingredient["health_impact_score"] * ingredient["percentage"] / 100
            total_scores["nutrient_density"] += ingredient["nutrient_density_score"] * ingredient["percentage"] / 100
            total_percentage += ingredient["percentage"]

        final_score = (
            total_scores["processing"] * weights["processing"] +
            total_scores["health_impact"] * weights["health_impact"] +
            total_scores["nutrient_density"] * weights["nutrient_density"]
        )
        return round(final_score, 2)

def main():
    analyzer = IngredientAnalyzer()
    
    # Example usage
    test_ingredients = "Potatoes, Vegetable Oil (Sunflower, Corn, or Canola), Salt, Spices"
    
    print("Analyzing ingredients:", test_ingredients)
    analysis = analyzer.analyze_ingredients(test_ingredients)
    
    if "error" not in analysis:
        print("\nAnalysis Results:")
        print(json.dumps(analysis, indent=2))
    else:
        print("Error:", analysis["error"])

if __name__ == "__main__":
    main()
    import os
    import json
    from openai import OpenAI
    from dotenv import load_dotenv
    from db_config import DatabaseConfig
    from models import User, Admin, IngredientAnalysis
    
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Initialize database
    db_config = DatabaseConfig()
    db = db_config.get_db()
    
    class IngredientAnalyzer:
        def __init__(self):
            self.categories = ["Natural", "Additives", "Preservatives", "Artificial Colors", "Highly Processed"]
            self.analysis_model = IngredientAnalysis(db)
            
            # Set up the system instruction
            self.system_instruction = """You are an AI specialized in analyzing food ingredients. Your task is to:
    
    1. Classify each ingredient into these categories:
       - Natural: Whole or minimally processed ingredients
       - Additives: Ingredients added for texture, flavor, or preservation
       - Preservatives: Chemicals for shelf life extension
       - Artificial Colors: Synthetic color enhancers
       - Highly Processed: Significantly altered ingredients
    
    2. Score each ingredient on a 1-5 scale for:
       - Processing Level (1=least processed, 5=most processed)
       - Health Impact (1=most healthy, 5=least healthy)
       - Nutrient Density (1=least nutritious, 5=most nutritious)
    
    3. Estimate the percentage of each ingredient based on typical formulations
    
    4. Return the analysis in this exact JSON format:
    {
      "ingredients": [
        {
          "name": string,
          "category": string,
          "processing_score": number,
          "health_impact_score": number,
          "nutrient_density_score": number,
          "percentage": number
        }
      ],
      "classification_summary": {
        "Natural": [string],
        "Additives": [string],
        "Preservatives": [string],
        "Artificial Colors": [string],
        "Highly Processed": [string]
      },
      "ingredient_percentages": {
        string: number
      },
      "health_score": number
    }
    
    Always return valid JSON that matches this exact format."""
        
        def analyze_ingredients(self, user_id, ingredients_text):
            try:
                # Create the chat completion using new API syntax
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.system_instruction},
                        {"role": "user", "content": f"Analyze these ingredients: {ingredients_text}"}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Extract JSON from response using new API syntax
                json_str = response.choices[0].message.content
                # Parse and validate JSON
                analysis = json.loads(json_str)
                
                # Calculate and update the health score
                if "ingredients" in analysis:
                    health_score = self.calculate_health_score(analysis)
                    analysis["health_score"] = health_score
                    
                    # Save analysis to database
                    analysis_id = self.analysis_model.save_analysis(user_id, ingredients_text, analysis)
                    analysis["analysis_id"] = analysis_id
                    
                return analysis
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON response"}
            except Exception as e:
                return {"error": f"Analysis failed: {str(e)}"}
    
        def calculate_health_score(self, ingredients_data):
            weights = {
                "processing": 0.5,
                "health_impact": 0.3,
                "nutrient_density": 0.2
            }
            
            total_scores = {"processing": 0, "health_impact": 0, "nutrient_density": 0}
            total_percentage = 0
    
            for ingredient in ingredients_data["ingredients"]:
                total_scores["processing"] += ingredient["processing_score"] * ingredient["percentage"] / 100
                total_scores["health_impact"] += ingredient["health_impact_score"] * ingredient["percentage"] / 100
                total_scores["nutrient_density"] += ingredient["nutrient_density_score"] * ingredient["percentage"] / 100
                total_percentage += ingredient["percentage"]
    
            final_score = (
                total_scores["processing"] * weights["processing"] +
                total_scores["health_impact"] * weights["health_impact"] +
                total_scores["nutrient_density"] * weights["nutrient_density"]
            )
            return round(final_score, 2)
    
        def get_user_analyses(self, user_id):
            return self.analysis_model.get_user_analyses(user_id)
    
        def get_analysis_by_id(self, analysis_id):
            return self.analysis_model.get_analysis_by_id(analysis_id)
    
    def main():
        # Initialize models
        user_model = User(db)
        admin_model = Admin(db)
        analyzer = IngredientAnalyzer()
        
        # Example: Create a test user
        try:
            user_id = user_model.create_user(
                username="test_user",
                email="test@example.com",
                password="test123"
            )
            print(f"Created test user with ID: {user_id}")
        except ValueError as e:
            print(f"User creation failed: {e}")
            # If user already exists, try to verify
            user = user_model.verify_user("test_user", "test123")
            if user:
                user_id = str(user['_id'])
                print(f"Using existing user with ID: {user_id}")
            else:
                print("Failed to create or verify user")
                return
    
        # Example usage
        test_ingredients = "Potatoes, Vegetable Oil (Sunflower, Corn, or Canola), Salt, Spices"
        
        print("Analyzing ingredients:", test_ingredients)
        analysis = analyzer.analyze_ingredients(user_id, test_ingredients)
        
        if "error" not in analysis:
            print("\nAnalysis Results:")
            print(json.dumps(analysis, indent=2))
            
            # Retrieve user's analysis history
            print("\nUser's Analysis History:")
            history = analyzer.get_user_analyses(user_id)
            for analysis in history:
                print(f"Analysis ID: {analysis['_id']}")
                print(f"Created at: {analysis['created_at']}")
                print(f"Ingredients: {analysis['ingredients_text']}")
                print("---")
        else:
            print("Error:", analysis["error"])
    
    if __name__ == "__main__":
        main()