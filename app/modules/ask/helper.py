from app.modules.ask.schema import AskRequest
from app.models.chatMessage.chatMessage import chatMessage
from agent import stream_graph_updates
from messageHandler import mongoManager
import asyncio
from app.modules.chat_history.helpers import get_last_n_human_messages


async def askHelper(reqParams: AskRequest):
    try:
        get = reqParams.dict()
        messagesColl = mongoManager.get_collection(chatMessage)
        chtmsg = chatMessage(**get)
        messagesColl.insert_one(chtmsg.dict(by_alias=True,exclude={'id'}))
        prevMessages = [(message.isHuman, message.message)for message in get_last_n_human_messages(reqParams.userId, reqParams.profile, 2)]
        aimessage = ""
        async for chunk in stream_graph_updates(reqParams.message,1,prevMessages, reqParams.profile):
            print(chunk, end="", flush=True)
            aimessage += chunk 
            yield chunk
        aiResp = chatMessage(**{
            "userId": reqParams.userId,
            "profile": reqParams.profile,
            "message": aimessage,
            "isHuman": False
        })
        messagesColl.insert_one(aiResp.dict(by_alias=True,exclude={'id'}))
    except Exception as e:
        raise Exception(e)


