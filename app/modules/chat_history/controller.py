from run import app
from flask import request
import json
from app.modules.chat_history.schema import ChatHistoryRequest
from app.modules.chat_history.helpers import get_chat_history_helper



@app.route('/chat_history', methods=['GET'])
def get_chat_history(): 
    reqParams = ChatHistoryRequest(**{
        "userId":request.json.get('userId'),
        "profile":request.json.get('profile')
        })
    msgs = get_chat_history_helper(reqParams)

    return json.dumps({
        "messages": [msg.dict(by_alias=True,exclude={'id'}) for msg in msgs],
        "size": len(msgs)
    })