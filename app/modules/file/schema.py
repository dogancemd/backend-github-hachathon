from pydantic import BaseModel


class FileRequest(BaseModel):
    userId: str
    payload: str
    filename: str
    extension: str