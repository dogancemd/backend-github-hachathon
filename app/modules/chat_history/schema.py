from pydantic import BaseModel


class ChatHistoryRequest(BaseModel):
    userId: str
    profile: str
    n: int


class ChatHistoryResponseMessage(BaseModel):
    text: str
    isUser: bool
    timestamp: str
    id: str
    @classmethod
    def from_chat_message(cls, chat_message):
        return cls(
            text=chat_message.message,
            isUser=chat_message.isHuman,
            timestamp=str(int(float(chat_message.dateCreated))),
            id = str(31)
        )