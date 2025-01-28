import pytesseract
import os
from PIL import Image
import sys

def test_tesseract():
    print("Python version:", sys.version)
    print("\nTesting Tesseract Installation:")
    print("-" * 50)

    # 1. Check Tesseract Path
    tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
    print(f"\n1. Tesseract Command Path: {tesseract_cmd}")
    print(f"   Path exists: {os.path.exists(tesseract_cmd)}")

    # 2. Check Tesseract Version
    try:
        version = pytesseract.get_tesseract_version()
        print(f"\n2. Tesseract Version: {version}")
    except Exception as e:
        print(f"\n2. Error getting Tesseract version: {str(e)}")

    # 3. List possible Tesseract paths
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        os.getenv('TESSERACT_PATH', ''),
        os.path.join(os.getcwd(), 'Tesseract-OCR', 'tesseract.exe')
    ]

    print("\n3. Checking possible Tesseract paths:")
    for path in possible_paths:
        if path:
            print(f"   {path}: {'Exists' if os.path.exists(path) else 'Not Found'}")

    # 4. Check if tesseract command is in PATH
    print("\n4. Checking system PATH:")
    system_paths = os.getenv('PATH', '').split(os.pathsep)
    tesseract_in_path = False
    for path in system_paths:
        tesseract_path = os.path.join(path, 'tesseract.exe')
        if os.path.exists(tesseract_path):
            print(f"   Found Tesseract in PATH: {tesseract_path}")
            tesseract_in_path = True
    if not tesseract_in_path:
        print("   Tesseract not found in system PATH")

if __name__ == "__main__":
    test_tesseract()
