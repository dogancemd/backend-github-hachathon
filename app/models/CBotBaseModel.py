from pydantic import BaseModel

class CBotBaseModel(BaseModel):
    @classmethod
    def get_collection_name(cls):
        pass

    @classmethod    
    def create_collection(db):
        pass