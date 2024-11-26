import os
from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
import requests
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dynamically set Tesseract path or use default
tesseract_path = os.environ.get('TESSERACT_PATH', '/usr/bin/tesseract')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        data = request.json
        image_url = data.get("image")
        
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400

        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({'error': 'Unable to fetch image from URL'}), 400

        img = Image.open(io.BytesIO(response.content))
        img = img.convert('L')
        img = img.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        try:
            extracted_text = pytesseract.image_to_string(img)
            tokens = re.findall(r'\b\w+\b', extracted_text)
            return jsonify({'text': extracted_text, 'tokens': tokens}), 200
        except Exception as ocr_error:
            return jsonify({
                'error': 'OCR Processing Failed',
                'details': str(ocr_error),
                'tesseract_path': pytesseract.pytesseract.tesseract_cmd
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
