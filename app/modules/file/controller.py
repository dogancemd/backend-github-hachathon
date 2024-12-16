from messageHandler import app
import base64
import os
import json
from app.modules.file.helpers import getFileName
import traceback
from rag_helper import load_voices, load_pdfs
from app.modules.file.schema import FileRequest
from app.models.common import UPLOAD_FOLDER
from fastapi import BackgroundTasks

def load_at_bg(profile, filename):
    if filename.endswith(".mp3"):
        load_voices(profile, [filename])
        print("Loaded voices")
    elif filename.endswith(".pdf"):
        load_pdfs(profile, [filename])
        print("Loaded pdfs")
    

@app.post('/file/{profile}')
def upload_base64(profile: str, fileReq: FileRequest, background_tasks: BackgroundTasks):
    print(FileRequest)
    # Get the JSON data containing the base64 string
    
    
    
    # Get the base64 string (assuming it's sent under the 'audio' key)
    file_data = fileReq.payload
    
    # Optional: If the file is prefixed with a base64 header (e.g., 'data:image/png;base64,...'),
    # remove the prefix if necessary
    if file_data.startswith('data:'):
        file_data = file_data.split(',')[1]
    
    # Decode the base64 string into binary data
    try:
        file_content = base64.b64decode(file_data)
    except Exception as e:
        raise Exception(f"Failed to decode the base64 string: {str(e)}")
    
    # Define a filename (You can customize this or get it from the request)
    filename = getFileName(fileReq.filename,profile)
    file_path = os.path.join(UPLOAD_FOLDER, profile, filename)
    if not os.path.isdir(os.path.join(UPLOAD_FOLDER, profile)):
        os.mkdir(os.path.join(UPLOAD_FOLDER, profile))
    # Save the decoded content to a file
    try:
        with open(file_path, 'wb') as file:
            file.write(file_content)
            background_tasks.add_task(load_at_bg, profile = profile, filename=filename)
            #load_voices(profile, [filename])
        return json.dumps({"isSucces": True})
    except Exception as e:
        print(e)
        return json.dumps({"isSuccess": False, "error": f"Failed to save the file: {str(e)}"})

