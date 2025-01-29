import os
import sys
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
import logging
import base64
from io import BytesIO
import traceback

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # Set Tesseract path directly
        self.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        if not os.path.exists(self.tesseract_cmd):
            raise EnvironmentError(f"Tesseract not found at {self.tesseract_cmd}")
        
        # Test Tesseract
        try:
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract version: {version}")
        except Exception as e:
            raise EnvironmentError(f"Error testing Tesseract: {str(e)}")

    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        gray = cv2.dilate(gray, kernel, iterations=1)
        
        # Apply blur to smooth out the edges
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return gray

    def extract_text_from_base64(self, base64_data):
        """Extract text from base64 encoded image data"""
        try:
            # Remove header if present
            if 'base64,' in base64_data:
                base64_data = base64_data.split('base64,')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            
            # Save original image for debugging
            debug_original = 'debug_original.png'
            image.save(debug_original)
            print(f"Saved original image: {debug_original}")
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Save processed image for debugging
            debug_processed = 'debug_processed.png'
            cv2.imwrite(debug_processed, processed_image)
            print(f"Saved processed image: {debug_processed}")
            
            # Extract text using different OCR configurations
            configs = [
                '--oem 3 --psm 6',  # Assume uniform block of text
                '--oem 3 --psm 4',  # Assume single column of text
                '--oem 3 --psm 3',  # Fully automatic page segmentation
            ]
            
            best_text = ""
            max_confidence = 0
            
            for config in configs:
                try:
                    print(f"Trying OCR with config: {config}")
                    
                    # Get text and confidence
                    data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                        text = pytesseract.image_to_string(processed_image, config=config)
                        
                        print(f"Confidence: {avg_confidence}")
                        print(f"Extracted text: {text[:100]}...")
                        
                        if avg_confidence > max_confidence and text.strip():
                            max_confidence = avg_confidence
                            best_text = text
                
                except Exception as e:
                    print(f"Error with config {config}: {str(e)}")
                    continue
            
            if not best_text.strip():
                raise ValueError("No text could be extracted from the image")
            
            print(f"Final extracted text: {best_text[:100]}...")
            return best_text.strip()
            
        except Exception as e:
            print(f"Error in extract_text_from_base64: {str(e)}")
            traceback.print_exc()
            raise

    def extract_text(self, image_path):
        """Extract text from an image file"""
        try:
            return self.extract_text_from_base64(base64.b64encode(open(image_path, 'rb').read()).decode())
        except Exception as e:
            print(f"Error in extract_text: {str(e)}")
            traceback.print_exc()
            raise