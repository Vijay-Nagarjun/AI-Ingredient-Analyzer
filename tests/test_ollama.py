import os
import sys
import json
import requests

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                'success': True,
                'models': models,
                'error': None
            }
    except Exception as e:
        return {
            'success': False,
            'models': None,
            'error': str(e)
        }

def analyze_ingredients(ingredients_text):
    """Test ingredient analysis with Ollama"""
    system_instruction = """You are an expert in analyzing food ingredients. Your task is to analyze the given ingredients and return a JSON response.

Rules:
1. ONLY return a valid JSON object, nothing else
2. The JSON must match this exact format:
{
  "ingredients": [
    {
      "name": "string",
      "category": "string",
      "processing_score": number,
      "health_impact_score": number,
      "nutrient_density_score": number,
      "percentage": number
    }
  ],
  "classification_summary": {
    "Natural": ["string"],
    "Additives": ["string"],
    "Preservatives": ["string"],
    "Artificial Colors": ["string"],
    "Highly Processed": ["string"]
  },
  "ingredient_percentages": {
    "string": number
  },
  "health_score": number
}

Instructions:
1. Classify each ingredient into one of these categories:
   - Natural: Whole or minimally processed ingredients
   - Additives: Ingredients added for texture, flavor, or preservation
   - Preservatives: Chemicals for shelf life extension
   - Artificial Colors: Synthetic color enhancers
   - Highly Processed: Significantly altered ingredients

2. Score each ingredient (1-5):
   - Processing Level: 1=least processed, 5=most processed
   - Health Impact: 1=most healthy, 5=least healthy
   - Nutrient Density: 1=least nutritious, 5=most nutritious

3. Estimate ingredient percentages (must sum to 100)

4. Calculate overall health score (0-100)

Remember: ONLY return the JSON object, no other text."""

    try:
        # Clean up ingredients text
        ingredients_text = ingredients_text.strip()
        if not ingredients_text:
            return {
                'success': False,
                'result': None,
                'error': "No ingredients provided"
            }
        
        # Create the Ollama API request
        payload = {
            "model": "llama3.2:3b",
            "prompt": f"{system_instruction}\n\nIngredients to analyze:\n{ingredients_text}\n\nResponse (JSON only):",
            "stream": False
        }
        
        print("Sending request to Ollama...")
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        
        if response.status_code != 200:
            return {
                'success': False,
                'result': None,
                'error': f"Ollama API error: {response.status_code}"
            }
        
        result = response.json()
        if 'response' not in result:
            return {
                'success': False,
                'result': None,
                'error': "Invalid response from Ollama"
            }
        
        # Try to extract JSON from the response
        json_str = result['response']
        
        # Clean up the response
        json_str = json_str.strip()
        if json_str.startswith('```json'):
            json_str = json_str[7:]
        if json_str.endswith('```'):
            json_str = json_str[:-3]
        
        try:
            analysis = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["ingredients", "classification_summary", "ingredient_percentages", "health_score"]
            missing_fields = [field for field in required_fields if field not in analysis]
            
            if missing_fields:
                return {
                    'success': False,
                    'result': None,
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            return {
                'success': True,
                'result': analysis,
                'error': None
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'result': json_str,
                'error': f"Failed to parse JSON: {str(e)}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'result': None,
            'error': str(e)
        }

if __name__ == "__main__":
    # Test Ollama connection
    print("Testing Ollama connection...")
    connection_result = test_ollama_connection()
    
    if connection_result['success']:
        print("Ollama is running")
        print("Available models:", [model['name'] for model in connection_result['models']])
    else:
        print("Failed to connect to Ollama:", connection_result['error'])
        sys.exit(1)
    
    # Test with sample ingredients
    print("\nTesting ingredient analysis...")
    sample_ingredients = """
    Ingredients: Water, Wheat Flour, Sugar, Vegetable Oil (Palm), Salt, 
    Yeast, Emulsifiers (E471, E481), Preservative (Calcium Propionate), 
    Antioxidant (Ascorbic Acid), Enzymes, Artificial Color (Yellow 5).
    """
    
    print("Input text:")
    print("-" * 50)
    print(sample_ingredients)
    print("-" * 50)
    
    result = analyze_ingredients(sample_ingredients)
    
    if result['success']:
        print("\nAnalysis result:")
        print("-" * 50)
        print(json.dumps(result['result'], indent=2))
        print("-" * 50)
    else:
        print("\nError occurred:")
        print(result['error'])
        if result['result']:
            print("\nRaw response:")
            print(result['result'])
