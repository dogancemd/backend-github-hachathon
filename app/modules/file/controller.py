from run import app
from flask import request, flash, redirect, url_for, jsonify
import base64
import os
import json
from app.modules.file.helpers import getFileName
import traceback




@app.route('/file/<profile>', methods=['POST'])
def upload_base64(profile: str):
    # Get the JSON data containing the base64 string
    data = request.get_json()
    
    
    # Ensure the base64 data exists in the request
    if 'audio' not in data:
        return jsonify({"error": "No file data provided"}), 400
    
    # Get the base64 string (assuming it's sent under the 'audio' key)
    file_data = data['audio']
    
    # Optional: If the file is prefixed with a base64 header (e.g., 'data:image/png;base64,...'),
    # remove the prefix if necessary
    if file_data.startswith('data:'):
        file_data = file_data.split(',')[1]
    
    # Decode the base64 string into binary data
    try:
        file_content = base64.b64decode(file_data)
    except Exception as e:
        return jsonify({"error": f"Failed to decode base64: {str(e)}"}), 400
    
    # Define a filename (You can customize this or get it from the request)
    filename = 'uploaded_file.wav'
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], profile, filename)
    if not os.path.isdir(os.path.join(app.config["UPLOAD_FOLDER"], profile)):
        os.mkdir(os.path.join(app.config["UPLOAD_FOLDER"], profile))
    # Save the decoded content to a file
    try:
        with open(file_path, 'wb') as file:
            file.write(file_content)
        return jsonify({"isSucces": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"isSuccess": False, "error": f"Failed to save the file: {str(e)}"}), 500


@app.route('/file/<profile>', methods = ['DELETE'])
def delete_file(profile:str):
    try:        
        filename = request.json.get("filename")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], profile, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        return app.response_class(
            response=json.dumps({"isSuccess": True}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=json.dumps({"isSuccess": False, "error": str(e)}),
            status=500,
            mimetype='application/json'
        )