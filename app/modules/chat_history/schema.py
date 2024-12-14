from pydantic import BaseModel


class ChatHistoryRequest(BaseModel):
    userId: str
    profile: str



