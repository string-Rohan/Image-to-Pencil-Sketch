import io
import cv2
import numpy as np
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

def convert_to_sketch(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted_image = 255 - gray_image
    blurred_image = cv2.GaussianBlur(inverted_image, (111, 111), 0)
    inverted_blurred = 255 - blurred_image
    return cv2.divide(gray_image, inverted_blurred, scale=230.0)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        # Read image directly from upload stream into memory
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Process image in memory
        sketch_img = convert_to_sketch(img)

        # Encode processed image to PNG in memory
        _, buffer = cv2.imencode('.png', sketch_img)
        io_buf = io.BytesIO(buffer)

        # Return file download directly from memory buffer
        return send_file(
            io_buf,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"sketch_{file.filename}"
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
