from app.modules.ask.helper import askHelper
from app.modules.ask.schema import AskRequest
from messageHandler import app
import json
import aio_pika
from datetime import datetime

@app.post("/ask")
async def prompt(askRequest: AskRequest):
    try:
        start_character = "[START]"
        await app.state.channel.default_exchange.publish (
            aio_pika.Message(body=start_character.encode()),
            routing_key="answer_queue"
        )
        async for answer in askHelper(askRequest):
            answer_json = {
                "id": askRequest.userId,
                "timestamp": str(int(datetime.utcnow().timestamp())),
                "text": answer,
                "isUser": False
            }
            body = json.dumps(answer_json)
            await app.state.channel.default_exchange.publish (
                aio_pika.Message(body=answer_json.get("text").encode()),
                routing_key="answer_queue"
            )
        end_character = "[END]"
        await app.state.channel.default_exchange.publish (
            aio_pika.Message(body=end_character.encode()),
            routing_key="answer_queue"
        )
        
    except Exception as e: 
        print(e)
        return {
            "success" : False,
            "error": str(e)
        }
    
    return { "success": True }