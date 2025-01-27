import os
import sys
import pytesseract
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.environ.get('TESSERACT_PATH', '')
        ]
        self.initialize_tesseract()

    def initialize_tesseract(self):
        """Initialize Tesseract with the correct path"""
        for path in self.tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract initialized with path: {path}")
                return True
        logger.error("Tesseract not found in any of the expected locations")
        return False

    def convert_to_bw(self, image):
        """Convert image to black and white with multiple methods"""
        if len(np.array(image).shape) == 3:
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        else:
            gray = np.array(image)
        
        # Resize image if too small
        min_width = 2000
        if gray.shape[1] < min_width:
            scale = min_width / gray.shape[1]
            width = int(gray.shape[1] * scale)
            height = int(gray.shape[0] * scale)
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
        
        versions = []
        
        # Version 1: Standard adaptive threshold
        blur1 = cv2.GaussianBlur(gray, (3, 3), 0)
        binary1 = cv2.adaptiveThreshold(
            blur1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        versions.append(("standard", binary1))
        
        # Version 2: More aggressive threshold
        blur2 = cv2.GaussianBlur(gray, (5, 5), 0)
        binary2 = cv2.adaptiveThreshold(
            blur2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 5
        )
        versions.append(("aggressive", binary2))
        
        return versions

    def enhance_contrast(self, image):
        """Enhance image contrast"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(2.0)

    def remove_noise_and_smooth(self, image):
        """Remove noise and smooth the image"""
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        return image

    def extract_text(self, image_path):
        """Extract text from image using multiple preprocessing methods"""
        try:
            # Open and enhance the image
            image = Image.open(image_path)
            enhanced_image = self.enhance_contrast(image)
            
            # Convert to different B&W versions
            versions = self.convert_to_bw(enhanced_image)
            
            best_text = ""
            max_confidence = 0
            
            # Try OCR on each version
            for version_name, img_version in versions:
                # Remove noise and smooth
                cleaned = self.remove_noise_and_smooth(img_version)
                
                # Extract text
                try:
                    text = pytesseract.image_to_string(cleaned)
                    
                    # Calculate confidence
                    data = pytesseract.image_to_data(cleaned, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    if avg_confidence > max_confidence:
                        max_confidence = avg_confidence
                        best_text = text
                    
                    logger.info(f"OCR {version_name} version confidence: {avg_confidence}")
                    
                except Exception as e:
                    logger.error(f"Error in OCR processing {version_name} version: {str(e)}")
                    continue
            
            if not best_text.strip():
                return {
                    'success': False,
                    'error': 'No text could be extracted from the image'
                }
            
            return {
                'success': True,
                'text': best_text.strip(),
                'confidence': max_confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
