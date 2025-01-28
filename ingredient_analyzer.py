import os
import json
import requests
from dotenv import load_dotenv
import numpy as np
import cv2
from PIL import Image
import pytesseract
import re

# Load environment variables
load_dotenv()

# Debug: Print the API key (first few characters)
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"API key loaded (first 5 chars): {api_key[:5]}...")
else:
    print("Warning: No API key found in environment variables!")

class IngredientAnalyzer:
    def __init__(self):
        self.categories = ["Natural", "Additives", "Preservatives", "Artificial Colors", "Highly Processed"]
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Set up the system instruction
        self.system_instruction = """Return a JSON object analyzing the ingredients. Format:
{
  "ingredients": [{"name": "string", "category": "string", "processing_score": 1-5, "health_impact_score": 1-5, "nutrient_density_score": 1-5}],
  "classification_summary": {"Natural": [], "Additives": [], "Preservatives": [], "Artificial Colors": [], "Highly Processed": []},
  "ingredient_percentages": {"category": 0-100},
  "health_score": 0-10
}

Categories: Natural (whole foods), Additives (flavor/texture), Preservatives, Artificial Colors, Highly Processed
Scores: Processing (1=least), Health (1=best), Nutrient (1=least), Overall (0-10, higher=better)

Return ONLY valid JSON."""
    
    def preprocess_image_for_ocr(self, image):
        """Apply preprocessing steps to improve OCR accuracy"""
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Resize image to have a minimum width while maintaining aspect ratio
        min_width = 2000
        if gray.shape[1] < min_width:
            scale = min_width / gray.shape[1]
            width = int(gray.shape[1] * scale)
            height = int(gray.shape[0] * scale)
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
        
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(gray, 11, 85, 85)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            13,
            3
        )
        
        # Create a copy for Otsu's method
        _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Process both versions
        for img in [binary, otsu]:
            # Remove small dots and noise
            kernel_small = np.ones((2,2), np.uint8)
            img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel_small)
            
            # Connect nearby text
            kernel_medium = np.ones((1,3), np.uint8)
            img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel_medium)
            
            # Remove noise in text
            img = cv2.bitwise_not(img)
            img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel_small)
            img = cv2.bitwise_not(img)
            
            # Final cleanup
            kernel_cleanup = np.ones((2,2), np.uint8)
            img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel_cleanup)
        
        # Add padding around both images
        padding = 50
        padded_binary = cv2.copyMakeBorder(
            binary,
            padding, padding, padding, padding,
            cv2.BORDER_CONSTANT,
            value=255
        )
        
        padded_otsu = cv2.copyMakeBorder(
            otsu,
            padding, padding, padding, padding,
            cv2.BORDER_CONSTANT,
            value=255
        )
        
        # Return both versions
        return Image.fromarray(padded_binary), Image.fromarray(padded_otsu)

    def extract_text_from_image(self, image_path, save_debug=False):
        """Extract text from image using improved OCR"""
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            processed_binary, processed_otsu = self.preprocess_image_for_ocr(image)
            
            # Save processed versions for debugging
            if save_debug:
                base_path = os.path.splitext(image_path)[0]
                processed_binary.save(f"{base_path}_binary.jpg")
                processed_otsu.save(f"{base_path}_otsu.jpg")
            
            # Configure Tesseract parameters
            custom_config = r'''--oem 3 --psm 6 
                -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789(),.% "
                -c tessedit_write_images=true
                -c page_separator=""'''
            
            # Try OCR on both versions
            text1 = pytesseract.image_to_string(
                processed_binary,
                config=custom_config
            )
            
            text2 = pytesseract.image_to_string(
                processed_otsu,
                config=custom_config
            )
            
            # Use the longer text (usually better quality)
            text = text1 if len(text1) > len(text2) else text2
            
            # Clean up the text
            text = text.strip()
            text = ' '.join(text.split())  # Remove extra whitespace
            text = text.replace('|', '')   # Remove vertical bars
            text = text.replace('�', '')   # Remove invalid characters
            
            # Try to identify ingredient list format
            if 'INGREDIENTS' in text.upper():
                text = text[text.upper().find('INGREDIENTS'):]
            elif 'INGRED' in text.upper():
                text = text[text.upper().find('INGRED'):]
            
            return {
                'success': True,
                'text': text,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'text': None,
                'error': str(e)
            }

    def analyze_ingredients(self, ingredients_text):
        """Analyze ingredients using Ollama"""
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
                "prompt": f"{self.system_instruction}\n\nIngredients to analyze:\n{ingredients_text}\n\nResponse (JSON only):",
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload)
            
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
            json_str = json_str.strip()
            
            # Remove any text before the first { and after the last }
            start_idx = json_str.find('{')
            end_idx = json_str.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                return {
                    'success': False,
                    'result': None,
                    'error': "No JSON object found in response"
                }
            
            json_str = json_str[start_idx:end_idx + 1]
            
            # Remove any markdown code block markers
            json_str = json_str.replace('```json', '').replace('```', '')
            
            # Remove any line comments
            json_str = '\n'.join(line for line in json_str.split('\n') if not line.strip().startswith('//'))
            
            # Remove any trailing commas before closing braces
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
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
                
                # Format percentages to 2 decimal places
                for category, percentage in analysis["ingredient_percentages"].items():
                    analysis["ingredient_percentages"][category] = round(percentage, 2)
                
                # Ensure health score is between 0-10
                if "health_score" in analysis:
                    analysis["health_score"] = min(10, max(0, analysis["health_score"] / 10))
                    analysis["health_score"] = round(analysis["health_score"], 1)
                
                # Add summary statistics
                analysis["summary"] = {
                    "total_ingredients": len(analysis["ingredients"]),
                    "natural_ingredients": len(analysis["classification_summary"].get("Natural", [])),
                    "artificial_ingredients": len(analysis["classification_summary"].get("Artificial Colors", [])) + 
                                          len(analysis["classification_summary"].get("Preservatives", [])),
                    "additives": len(analysis["classification_summary"].get("Additives", [])),
                }
                
                return {
                    'success': True,
                    'result': analysis,
                    'error': None
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'result': None,
                    'error': f"Failed to parse JSON: {str(e)}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }

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
        print(json.dumps(analysis['result'], indent=2))
    else:
        print("Error:", analysis["error"])

if __name__ == "__main__":
    main()