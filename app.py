from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import cv2
import numpy as np
import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from flask_session import Session
from oauthlib.oauth2 import BackendApplicationClient
from document_scanner import scan_document


# Disable OAuthlib's HTTPS requirement for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
app.secret_key = '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'  # Replace with your secret key

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# OAuth 2.0 setup
CLIENT_SECRETS_FILE = 'client_secret_463353779143-f9lil5vjgvrrklp0fh3323hf1luidh6l.apps.googleusercontent.com.json'  # Replace with the path to your credentials.json file
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Route to initiate OAuth 2.0 flow
@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

# Route to handle OAuth 2.0 callback
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('index'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# Route to render index.html template
@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect('authorize')
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

    # Upload the processed image to Google Drive
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': 'processed_image.jpg'}
    media = MediaFileUpload(processed_image_path, mimetype='image/jpeg')
    drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
