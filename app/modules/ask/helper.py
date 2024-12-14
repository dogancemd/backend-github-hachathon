from app.modules.ask.schema import AskRequest
from run import mongoManager
from app.models.chatMessage.chatMessage import chatMessage


def askHelper(reqParams: AskRequest):
    try:
        get = reqParams.dict()
        messagesColl = mongoManager.get_collection(chatMessage)
        chtmsg = chatMessage(**get)
        print(chtmsg)
        messagesColl.insert_one(chtmsg.dict(by_alias=True,exclude={'id'}))
        return "Message saved"
    except Exception as e:
        return str(e)


