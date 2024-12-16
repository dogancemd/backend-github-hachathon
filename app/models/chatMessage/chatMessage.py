from pydantic import Field
from datetime import datetime
from typing import Optional
from pymongo.database import Database
from app.models.CBotBaseModel import CBotBaseModel
from app.models.CBotObjectId import CBotObjectId

class chatMessage(CBotBaseModel):
    __collection_name__ = "ChatMessages"
    id: Optional[CBotObjectId] = Field(None, alias="_id")
    userId: str
    profile: str
    message: str
    dateCreated: Optional[str] = Field(default_factory=datetime.utcnow().timestamp().__str__)
    isHuman: bool = True 
    
    @classmethod
    def get_collection_name(cls):
        return cls.__collection_name__
        

    @classmethod
    def create_collection(db: Database):
        try:
            coll_name = chatMessage.get_collection_name()
            db.create_collection(coll_name, {})
        except:    # collection already exists
            pass
        collection = db.get_collection(coll_name)
        collection.create_index("userId")
        collection.create_index("profile")
        collection.create_index("dateCreated")
