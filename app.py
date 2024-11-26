from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
import requests
import re  # For tokenization
from flask_cors import CORS
import os
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dynamically detect or configure Tesseract path
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    # If not found, use an environment variable as a fallback
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        data = request.json
        
        # Check if an image file or URL is provided in the request
        image_url = data.get("image")
        if image_url:
            response = requests.get(image_url)
            if response.status_code != 200:
                return jsonify({'error': 'Unable to fetch image from URL'}), 400
            img = Image.open(io.BytesIO(response.content))
        
        # Apply image processing
        img = img.convert('L')  # Convert to grayscale
        img = img.filter(ImageFilter.MedianFilter())  # Apply median filter
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)  # Enhance contrast
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(img)
        
        # Tokenize text: Split into words (ignores punctuation and splits on spaces)
        tokens = re.findall(r'\b\w+\b', extracted_text)
        
        return jsonify({'text': extracted_text, 'tokens': tokens}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
