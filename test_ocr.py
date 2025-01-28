import pytesseract
from PIL import Image
import os
import sys
from io import BytesIO
import requests

def test_with_sample_image():
    print("Testing OCR with a sample image...")
    
    # Set Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Create a test image with text using PIL
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a new image with a white background
    img = Image.new('RGB', (400, 100), color='white')
    d = ImageDraw.Draw(img)
    
    # Add some text to the image
    text = "Test Ingredients: Water, Sugar, Salt"
    d.text((10,10), text, fill=(0,0,0))
    
    # Save the test image
    test_image_path = 'test_image.png'
    img.save(test_image_path)
    
    try:
        # Try to read the text from the image
        print("\nTrying to read text from test image...")
        result = pytesseract.image_to_string(Image.open(test_image_path))
        print("\nExtracted text:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        if result.strip():
            print("\n✓ Success! Tesseract successfully extracted text from the image.")
        else:
            print("\n✗ Error: No text was extracted from the image.")
            
    except Exception as e:
        print(f"\n✗ Error during OCR: {str(e)}")
    
    print("\nTesseract Configuration:")
    print(f"Path: {pytesseract.pytesseract.tesseract_cmd}")
    print(f"Path exists: {os.path.exists(pytesseract.pytesseract.tesseract_cmd)}")
    
    try:
        version = pytesseract.get_tesseract_version()
        print(f"Version: {version}")
    except Exception as e:
        print(f"Error getting version: {str(e)}")

if __name__ == "__main__":
    test_with_sample_image()
