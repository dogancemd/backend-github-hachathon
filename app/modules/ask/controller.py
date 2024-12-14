from app.modules.ask.helper import askHelper
from app.modules.ask.schema import AskRequest
from messageHandler import app
import json
import aio_pika


@app.get("/ask")
async def prompt(askRequest: AskRequest):
    try:
        async for answer in askHelper(askRequest):
            answer_json = {
                "answer": answer,
                "userId": askRequest.userId,
                "is_end": False
            }
            body = json.dumps(answer_json)
            await app.state.channel.default_exchange.publish (
                aio_pika.Message(body=body.encode()),
                routing_key="answer_queue"
            )
        answer_json = {
            "userId": askRequest.userId,
            "is_end": True
        }
        body = json.dumps(answer_json)
        await app.state.channel.default_exchange.publish (
            aio_pika.Message(body=body.encode()),
            routing_key="answer_queue"
        )
        
    except Exception as e: 
        print(e)
        return {
            "success" : False,
            "error": str(e)
        }
    
    return { "success": True }