from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
import re
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup logging
logging.basicConfig(level=logging.INFO)
app.logger.info('App is starting...')

def preprocess_image(image):
    """
    Apply various image processing techniques to improve OCR accuracy
    """
    # Convert to RGB if image is in RGBA mode
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Convert to grayscale
    image = image.convert('L')
    
    # Apply noise reduction
    image = image.filter(ImageFilter.MedianFilter(3))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    # Apply sharpening
    image = image.filter(ImageFilter.SHARPEN)
    
    # Increase image size if too small
    if image.width < 1000 or image.height < 1000:
        ratio = max(1000 / image.width, 1000 / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    return image

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        # Check if image file is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Read and process the image
        img = Image.open(io.BytesIO(image_file.read()))
        
        # Apply image preprocessing
        processed_img = preprocess_image(img)
        
        # Perform OCR with custom configuration
        custom_config = r'--oem 3 --psm 6'  # Use LSTM OCR Engine Mode with automatic page segmentation
        extracted_text = pytesseract.image_to_string(processed_img, config=custom_config)
        
        # Tokenize text
        # Split into words, convert to lowercase, and remove special characters
        tokens = re.findall(r'\b\w+\b', extracted_text.lower())
        
        # Remove very short tokens (likely noise)
        tokens = [token for token in tokens if len(token) > 1]
        
        # Create response with both raw text and processed tokens
        response = {
            'raw_text': extracted_text,
            'tokens': tokens,
            'token_count': len(tokens)
        }
        
        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return jsonify({'error': str(e), 'type': str(type(e))}), 500

@app.route('/test')
def test():
    return "hello"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
