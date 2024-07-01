from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import cv2
import numpy as np
import os
from flask_session import Session
from document_scanner import scan_document

app = Flask(__name__)
app.secret_key = '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'  # Replace with your secret key

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Route to render index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Route to receive image data and process it
@app.route('/upload', methods=['POST'])
def upload():
    # Get the image file from POST request
    file = request.files['image']

    # Read the image file
    img_np = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    # Process image using document scanner logic
    processed_image = scan_document(img)

    # Save processed image locally
    processed_image_path = 'static/processed_image.jpg'
    cv2.imwrite(processed_image_path, processed_image)

    return jsonify({'result': 'success', 'image_url': processed_image_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
