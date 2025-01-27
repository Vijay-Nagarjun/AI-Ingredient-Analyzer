import os
import sys
from PIL import Image
import pytesseract
import cv2
import numpy as np
import json
import requests

# Add parent directory to path to import ingredient_analyzer
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from ingredient_analyzer import IngredientAnalyzer

def test_complete_pipeline():
    """Test the complete pipeline from image to analysis"""
    print("Testing complete pipeline...")
    
    # Initialize analyzer
    analyzer = IngredientAnalyzer()
    
    # Test image path
    image_path = os.path.join(parent_dir, "testing_images/IMG20241219191815[1].jpg")
    print(f"Input image: {image_path}")
    print("=" * 50)
    
    # Step 1: Extract text from image
    print("Step 1: OCR Text Extraction")
    print("-" * 50)
    
    ocr_result = analyzer.extract_text_from_image(image_path, save_debug=True)
    if not ocr_result['success']:
        print(f"OCR failed: {ocr_result['error']}")
        return
    
    extracted_text = ocr_result['text']
    print("Extracted text:")
    print(extracted_text)
    print("-" * 50)
    print()
    
    # Step 2: Analyze ingredients
    print("Step 2: Ingredient Analysis")
    print("-" * 50)
    
    analysis_result = analyzer.analyze_ingredients(extracted_text)
    if not analysis_result['success']:
        print(f"Analysis failed: {analysis_result['error']}")
        return
    
    print("Analysis result:")
    print(json.dumps(analysis_result['result'], indent=2))

if __name__ == "__main__":
    test_complete_pipeline()
