from pydantic import BaseModel
from datetime import datetime



class User(BaseModel):
    id: str
    name: str
    create_date: datetime
    update_date: datetime


class Token(BaseModel):
    token_type: str = 'bearer'
    access_token: str = None


class TokenData(BaseModel):
    username: str | None = None
