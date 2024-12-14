import pymongo
from pymongo.database import Database
from app.models.CBotBaseModel import CBotBaseModel

class MongoDBManager:
    def __init__(self,db_name):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db_name = db_name
        
    def get_db(self):
        return self.client[self.db_name]
    
    def get_collection(self, collection_type: CBotBaseModel):
        db = self.get_db()
        try:
            return db.get_collection(collection_type.get_collection_name())
        except:
            collection_type.create_collection(db)
            return db.get_collection(collection_type.get_collection_name())
            

    def start_transaction(self):
        return self.client.start_session()

