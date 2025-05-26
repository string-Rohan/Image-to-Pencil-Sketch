from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SKETCH_FOLDER'] = 'sketches'

# Ensure upload and sketch folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SKETCH_FOLDER'], exist_ok=True)

def convert_to_sketch(image_path, sketch_path):
    # Load the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Invert the grayscale image
    inverted_image = 255 - gray_image
    
    # Blur the inverted image
    blurred_image = cv2.GaussianBlur(inverted_image, (111, 111), 0)
    
    # Invert the blurred image
    inverted_blurred = 255 - blurred_image
    
    # Sketch effect (divide grayscale image by inverted blurred image)
    sketch_image = cv2.divide(gray_image, inverted_blurred, scale=230.0)
    
    # Save the sketch
    cv2.imwrite(sketch_path, sketch_image)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        
        # Save the uploaded file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(upload_path)
        
        # Convert the image to a sketch
        sketch_filename = f"sketch_{file.filename}"
        sketch_path = os.path.join(app.config['SKETCH_FOLDER'], sketch_filename)
        convert_to_sketch(upload_path, sketch_path)
        
        # Provide the sketch for download
        return render_template('index.html', sketch_filename=sketch_filename)
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    sketch_path = os.path.join(app.config['SKETCH_FOLDER'], filename)
    return send_file(sketch_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)