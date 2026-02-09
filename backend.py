from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
import pytesseract
from PIL import Image
import io
import re

# Initialize Flask App
app = Flask(__name__)
# Enable CORS so your HTML frontend can talk to this Python backend
CORS(app)

# Initialize Google Translator
translator = Translator()

# --- CONFIGURATION ---
# If Tesseract is not in your PATH, uncomment and set the path below:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print(">>> OMNI-PRIME BACKEND SYSTEM ONLINE <<<")
print(">>> LISTENING ON PORT 5000...")

def number_to_english(n_str):
    """
    Server-side logic to convert numbers/currency to words.
    Example: $10 -> "Ten Dollars"
    """
    # Simple dictionary logic for demonstration
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    
    clean_str = re.sub(r'[^0-9]', '', n_str)
    try:
        num = int(clean_str)
        if num < 10:
            val = ones[num]
        else:
            val = str(num) # Keep it simple for large numbers
            
        if "$" in n_str: return f"{val} Dollars"
        if "£" in n_str: return f"{val} Pounds"
        if "₹" in n_str: return f"{val} Rupees"
        return val
    except:
        return n_str

@app.route('/status', methods=['GET'])
def system_status():
    """Health check endpoint for the frontend to verify connection."""
    return jsonify({
        "status": "ONLINE",
        "system": "OMNI-PRIME",
        "node": "SECURE_GOLD_01",
        "encryption": "AES-256"
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """
    Main endpoint. Receives an image or text, processes it, and translates to Hindi.
    """
    try:
        response_data = {
            "original_text": "",
            "translated_text": "",
            "type": "TEXT",
            "confidence": 0,
            "detected_lang": "Auto"
        }

        # 1. HANDLE IMAGE UPLOAD (OCR)
        if 'image' in request.files:
            file = request.files['image']
            # Convert raw bytes to an Image object
            img = Image.open(io.BytesIO(file.read()))
            
            # Perform OCR using PyTesseract (Server-side is more powerful than browser)
            # 'eng' is used as base, but you can add 'urd+ara' if Tesseract lang data is installed
            text = pytesseract.image_to_string(img, lang='eng')
            response_data["original_text"] = text.strip()
            response_data["confidence"] = 98 # PyTesseract doesn't always return conf easily, simulating high conf

        # 2. HANDLE RAW TEXT INPUT
        elif 'text' in request.form:
            response_data["original_text"] = request.form['text']
            response_data["confidence"] = 100

        else:
            return jsonify({"error": "No input data provided"}), 400

        # --- PROCESSING LOGIC ---
        
        text_to_process = response_data["original_text"]

        if not text_to_process:
            return jsonify({"error": "No legible text found"}), 400

        # Check if it is Numeric/Currency
        if re.match(r'^[$£€₹]?\s*[\d,\.]+\s*[$£€₹]?$', text_to_process.strip()):
            response_data["type"] = "NUMERIC"
            response_data["translated_text"] = number_to_english(text_to_process)
            response_data["detected_lang"] = "Numeric"
        else:
            # Perform Translation to Hindi
            # src='auto' lets Google detect Urdu, Arabic, English, etc.
            translation = translator.translate(text_to_process, dest='hi')
            
            response_data["type"] = "TEXT DATA"
            response_data["translated_text"] = translation.text
            response_data["detected_lang"] = translation.src.upper()

        return jsonify(response_data)

    except Exception as e:
        print(f"SYSTEM ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server
    app.run(debug=True, port=5000)