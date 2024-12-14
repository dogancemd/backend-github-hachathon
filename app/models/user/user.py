from app.models.CBotBaseModel import CBotBaseModel
from app.models.CBotObjectId import CBotObjectId
from typing import Optional, List
from pydantic import Field


class User(CBotBaseModel):
    id: Optional[CBotObjectId] = Field(default_factory=CBotBaseModel,alias="_id")
    profiles: List[str]