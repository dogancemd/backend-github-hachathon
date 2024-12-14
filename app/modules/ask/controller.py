from run import app
from flask import request
import json
from app.modules.ask.schema import AskRequest
from app.modules.ask.helper import askHelper

@app.route('/ask', methods=['GET'])
def ask():
    reqParams = AskRequest(**{
        "userId": request.json.get('userId'),
        "profile": request.json.get('profile'),
        "message": request.json.get('message')
    })
    response = askHelper(reqParams)
    return app.response_class(
        response=json.dumps({"message": response}),
        status=200,
        mimetype='application/json'
    )