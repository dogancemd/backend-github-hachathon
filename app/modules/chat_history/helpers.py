from app.modules.chat_history.schema import ChatHistoryRequest
from app.models.chatMessage.chatMessage import chatMessage  
from pymongo.database import Database
from run import mongoManager
def get_last_n_human_messages(userId: str, profile: str, n: int):
    messageColl = mongoManager.get_collection(chatMessage)
    messageCollSize = messageColl.count_documents({"userId": userId, "profile": profile, "isHuman": True})
    n = min(n, messageCollSize)
    messageCurr = messageColl.aggregate([{"$match": {"userId": userId, "profile": profile, "isHuman": True}},{"$sort": {"dateCreated": -1}}, {"$skip": n-1}, {"$limit": 1}]) 
    result = list()
    isMessage = False
    for message in messageCurr:  
        isMessage = True
        msg = message
        break
    if isMessage:
        date = msg["dateCreated"]
        messageCurr = messageColl.aggregate([
            {"$match" : {"userId": userId, "profile": profile, "dateCreated": date}},
            {"$project": {"_id": 0}}
        ])
        for mess in messageCurr:
            result.append(chatMessage(**mess))
        return result
    else:
        return []
    
def get_last_n_messages(userId: str, profile: str, n: int):
    messageColl = mongoManager.get_collection(chatMessage)
    messageCollSize = messageColl.count_documents({"userId": userId, "profile": profile})
    n = min(n, messageCollSize)
    messageCurr = messageColl.aggregate([{"$match": {"userId": userId, "profile": profile}},{"$sort": {"dateCreated": -1}}, {"$limit": n}]) 
    result = list()
    for msg in messageCurr:
        date = msg["dateCreated"]
        messageCurr = messageColl.aggregate([
            {"$match" : {"userId": userId, "profile": profile, "dateCreated": date}},
            {"$project": {"_id": 0}}
        ])
        for mess in messageCurr:
            result.append(chatMessage(**mess))
        return result
    else:
        return []
    


def get_chat_history_helper(reqParams: ChatHistoryRequest):
    return get_last_n_messages(reqParams.userId, reqParams.profile, reqParams.n)
