import io
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

def convert_to_sketch(img):
    # Convert to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Invert the grayscale image
    inverted_image = 255 - gray_image
    
    # Blur the inverted image
    blurred_image = cv2.GaussianBlur(inverted_image, (111, 111), 0)
    
    # Invert the blurred image
    inverted_blurred = 255 - blurred_image
    
    # Calculate sketch effect
    return cv2.divide(gray_image, inverted_blurred, scale=230.0)

@app.route('/', methods=['GET', 'POST'])
def index():
    sketch_data = None
    filename = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        # Read image directly from upload stream into memory
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Generate sketch in memory
        sketch_img = convert_to_sketch(img)

        # Encode processed image to PNG buffer
        _, buffer = cv2.imencode('.png', sketch_img)
        
        # Convert buffer to Base64 string for direct HTML display/download
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        sketch_data = f"data:image/png;base64,{encoded_img}"
        filename = f"sketch_{file.filename}"

    return render_template('index.html', sketch_data=sketch_data, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
