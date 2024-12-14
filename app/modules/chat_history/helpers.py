from app.modules.chat_history.schema import ChatHistoryRequest
from app.models.chatMessage.chatMessage import chatMessage  
from pymongo.database import Database
from run import mongoManager
def get_last_n_human_messages(userId: str, profile: str, n: int):
    messageColl = mongoManager.get_collection(chatMessage)
    messageCurr = messageColl.aggregate([{"$match": {"userId": userId, "profile": profile, "isHuman": True}},{"$sort": {"dateCreated": -1}}, {"$skip": n-1}, {"$limit": 1}]) 
    result = list()
    isMessage = False
    for message in messageCurr:  
        isMessage = True
        msg = message
        break
    if isMessage:
        date = msg["dateCreated"]
        print(type(date))
        messageCurr = messageColl.aggregate([
            {"$match" : {"userId": userId, "profile": profile, "dateCreated": date}}
        ])
        print(messageCurr is None)
        for mess in messageCurr:
            result.append(mess)
        return result
    else:
        return []
    



def get_chat_history_helper(reqParams: ChatHistoryRequest):
    return get_last_n_human_messages(reqParams.userId, reqParams.profile, 2)
