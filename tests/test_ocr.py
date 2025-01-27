import os
import sys
import pytesseract
from PIL import Image, ImageEnhance
import numpy as np
import cv2

def enhance_text_regions(image):
    """Enhance text regions in the image"""
    # Find text-like regions using edge detection
    edges = cv2.Canny(image, 100, 200)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,1))
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # Find contours of text regions
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create mask of text regions
    mask = np.zeros_like(image)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if aspect_ratio > 2:  # Likely a text line
            cv2.rectangle(mask, (x-5, y-5), (x+w+5, y+h+5), 255, -1)
    
    # Apply mask to original image
    return cv2.bitwise_and(image, mask)

def remove_noise(binary):
    """Remove noise while preserving text"""
    # Remove small dots
    kernel_small = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
    
    # Connect nearby text
    kernel_medium = np.ones((2,3), np.uint8)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_medium)
    
    # Remove noise in text
    cleaned = cv2.bitwise_not(cleaned)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_small)
    cleaned = cv2.bitwise_not(cleaned)
    
    # Final cleanup
    kernel_cleanup = np.ones((3,3), np.uint8)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel_cleanup)
    
    return cleaned

def try_multiple_thresholds(gray):
    """Try different thresholding methods"""
    results = []
    
    # Adaptive Gaussian
    binary1 = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    results.append(binary1)
    
    # Adaptive Mean
    binary2 = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    results.append(binary2)
    
    # Otsu's method
    _, binary3 = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    results.append(binary3)
    
    return results

def preprocess_image(image):
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

def extract_text(image_path):
    """Extract text from image using Tesseract OCR"""
    try:
        # Load and preprocess image
        image = Image.open(image_path)
        processed_binary, processed_otsu = preprocess_image(image)
        
        # Save processed versions for inspection
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

if __name__ == "__main__":
    # Test with sample image
    test_image = "Y:/Final year project/Pcode/AI-Ingredient-Analyzer/testing_images/IMG20241219191815[1].jpg"
    
    print("Testing OCR component...")
    print(f"Input image: {test_image}")
    
    result = extract_text(test_image)
    
    if result['success']:
        print("\nExtracted text:")
        print("-" * 50)
        print(result['text'])
        print("-" * 50)
    else:
        print("\nError occurred:")
        print(result['error'])
