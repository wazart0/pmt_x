from typing import Optional, Dict, List
from pydantic import BaseModel
from sqlmodel import Field, ARRAY, SQLModel, create_engine, Column, Float, JSON, BINARY, TIMESTAMP, text, UUID

from datetime import datetime
import uuid as uuid_pkg

# import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


from src.utils import get_password_hash, verify_password





def _newid():
    return uuid_pkg.uuid4()


def _isid(id):
    UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    return bool(UUID_PATTERN.match(id))


class Base(SQLModel):
    id: Optional[uuid_pkg.UUID] = Field(default=None, sa_type=UUID, 
        sa_column_kwargs={
            'primary_key': True,
            'index': True,
            'nullable': False,
            'server_default': text("gen_random_uuid()")
    })
    created_datetime: Optional[datetime] = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True), 
        sa_column_kwargs={
            'nullable': False,
            'server_default': text("CURRENT_TIMESTAMP")
    })
    updated_datetime: Optional[datetime] = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True), 
        sa_column_kwargs={
            'nullable': False,
            'server_default': text("CURRENT_TIMESTAMP"),
            'server_onupdate': text("CURRENT_TIMESTAMP")
    })

    def __repr__(self) -> str:
        return f'User(id={str(self.id)!r}, create_date={self.create_date.isoformat()!r}, update_date={self.update_date.isoformat()!r})'



class UserBase(SQLModel):
    name: str
    username: str = Field(unique=True, index=True)


class UserHiddenBase(UserBase):
    password: str


class User(Base, UserHiddenBase, table=True):
    pass


class UserCreate(UserHiddenBase):
    pass


class UserRead(Base, UserBase):
    pass


class UserUpdate(SQLModel):
    id: uuid_pkg.UUID
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    

class TaskBase(SQLModel):
    name: str
    description: str
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text("'{}'::jsonb")
    ))


class Task(Base, TaskBase, table=True):
    pass


class TaskCreate(TaskBase):
    pass


class TaskRead(Base, TaskBase):
    pass


class TaskUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    doc: Optional[Dict] = None



class BaselineBase(SQLModel):
    name: str
    description: str
    tasks: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text("'{}'::jsonb")
    ))
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text("'{}'::jsonb")
    ))


class Baseline(Base, BaselineBase, table=True):
    pass


class BaselineCreate(BaselineBase):
    pass


class BaselineRead(Base, BaselineBase):
    pass


class BaselineUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tasks: Optional[Dict] = None
    doc: Optional[Dict] = None



class UserViewBase(SQLModel):
    name: str
    user_id: uuid_pkg.UUID = Field(default=None, foreign_key='user.id')
    filter: str
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text("'{}'::jsonb")
    ))


class UserView(Base, UserViewBase, table=True):
    pass


class UserViewCreate(UserViewBase):
    pass


class UserViewRead(Base, UserViewBase):
    pass


class UserViewUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter: Optional[str] = None
    doc: Optional[Dict] = None



class Token(BaseModel):
    token_type: str = 'bearer'
    access_token: str = None


class TokenData(BaseModel):
    username: str | None = None

