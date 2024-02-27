from src.database import pg_url


from typing import Optional, Dict, List
from sqlmodel import Field, ARRAY, SQLModel, create_engine, Column, Float, JSON, BINARY


import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB



class Hero1(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None
    
    array: List[float] = Field(sa_column=Column(ARRAY(Float)))
    meta: Dict = Field(default={}, sa_column=sa.Column(sa.JSON().with_variant(JSONB(), 'postgresql')))


    # data: dict = Field(sa_column=Column(JSON), default={})

    class Config:
        arbitrary_types_allowed = True 


engine = create_engine(pg_url)

SQLModel.metadata.create_all(engine)
