from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
import re
from flask_cors import CORS

# Uncomment and set path if needed on Windows
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
CORS(app, resources={r"/process-image": {"origins": "*"}})

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
        
        # Print file details for debugging
        print(f"Received file: {image_file.filename}")
        print(f"Content type: {image_file.content_type}")
        
        # Read and process the image
        img = Image.open(io.BytesIO(image_file.read()))
        
        # Print image details
        print(f"Image mode: {img.mode}")
        print(f"Image size: {img.size}")
        
        # Apply image preprocessing
        processed_img = preprocess_image(img)
        
        # Perform OCR with custom configuration
        custom_config = r'--oem 3 --psm 6'  # Use LSTM OCR Engine Mode with automatic page segmentation
        extracted_text = pytesseract.image_to_string(processed_img, config=custom_config)
        
        print(f"Extracted text: {extracted_text}")
        
        # Tokenize text
        # Split into words, convert to lowercase, and remove special characters
        tokens = re.findall(r'\b\w+\b', extracted_text.lower())
        
        # Remove very short tokens (likely noise)
        tokens = [token for token in tokens if len(token) > 1]
        
        print(f"Tokens: {tokens}")
        
        # Create response with both raw text and processed tokens
        response = {
            'raw_text': extracted_text,
            'tokens': tokens,
            'token_count': len(tokens)
        }
        
        return jsonify(response), 200
    except Exception as e:
        # Log the full traceback
        import traceback
        print(f"Error processing image: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e), 
            'type': str(type(e)),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/test')
def get_test():
    return 'HELLO'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
