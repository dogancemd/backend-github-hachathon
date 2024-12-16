from pydantic import BaseModel



class AskRequest(BaseModel):
    userId: str
    message: str 
    profile: str