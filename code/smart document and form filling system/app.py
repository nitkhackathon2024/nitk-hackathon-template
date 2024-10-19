import os
import sys
import logging
import tempfile
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import pytesseract
from pytesseract import Output
from pytesseract.pytesseract import TesseractNotFoundError
import cv2
import re

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure the output directory exists
output_dir = os.path.join(os.getcwd(), 'output')
os.makedirs(output_dir, exist_ok=True)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('registration.html')  # Render the registration form

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Check if the post request has the image file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            # Save the uploaded file temporarily
            temp_filename = os.path.join(tempfile.gettempdir(), file.filename)
            file.save(temp_filename)

            # Perform OCR processing
            image = cv2.imread(temp_filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)

            # Clean up the temporary file
            os.remove(temp_filename)

            # Parse the text to fill out the form
            form_data = parse_ocr_text(text)

            return jsonify({'data': form_data})
        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except TesseractNotFoundError as e:
        logger.error(f"Tesseract OCR not found: {str(e)}")
        return jsonify({'error': 'Tesseract OCR is not properly installed. Please contact support.'}), 500
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500

def parse_ocr_text(text):
    # Use regex to extract specific fields from the OCR text
    form_data = {
        'firstname': '',
        'middlename': '',
        'lastname': '',
        'phone': '',
        'address': '',
        'email': ''
    }

    # Example regex patterns to extract the fields
    name_pattern = re.compile(r'First Name:\s*(\S+)\s*Middle Name:\s*(\S+)?\s*Last Name:\s*(\S+)')
    phone_pattern = re.compile(r'Phone Number:\s*(\+?\d{1,4}[-\s]?(\d{1,4}[-\s]?){2,3}\d{1,4})')
    address_pattern = re.compile(r'Current Address:\s*(.*)')
    email_pattern = re.compile(r'Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')

    # Extract names
    name_match = name_pattern.search(text)
    if name_match:
        form_data['firstname'] = name_match.group(1)
        form_data['middlename'] = name_match.group(2) if name_match.group(2) else ''
        form_data['lastname'] = name_match.group(3)

    # Extract phone number
    phone_match = phone_pattern.search(text)
    if phone_match:
        form_data['phone'] = phone_match.group(1)

    # Extract address
    address_match = address_pattern.search(text)
    if address_match:
        form_data['address'] = address_match.group(1).strip()

    # Extract email
    email_match = email_pattern.search(text)
    if email_match:
        form_data['email'] = email_match.group(1)

    return form_data

if __name__ == '__main__':
    app.run(debug=True)
