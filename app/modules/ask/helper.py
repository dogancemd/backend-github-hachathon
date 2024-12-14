from app.modules.ask.schema import AskRequest
from app.models.chatMessage.chatMessage import chatMessage
from agent import stream_graph_updates
from app.models.mongoDBmanager import MongoDBManager
import asyncio


mongoManager = MongoDBManager("Chat")

async def askHelper(reqParams: AskRequest):
    try:
        get = reqParams.dict()
        messagesColl = mongoManager.get_collection(chatMessage)
        chtmsg = chatMessage(**get)
        messagesColl.insert_one(chtmsg.dict(by_alias=True,exclude={'id'}))
        print("Message inserted")
        async for chunk in stream_graph_updates(reqParams.message,1):
            print(chunk, end="", flush=True)
            yield chunk
        print("Message sent to graph")
    except Exception as e:
        raise Exception(e)


