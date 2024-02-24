from pydantic import BaseModel
from datetime import datetime



class User(BaseModel):
    id: str
    name: str
    create_date: datetime
    update_date: datetime

