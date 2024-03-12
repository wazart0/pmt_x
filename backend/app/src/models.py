from typing import Optional, Dict, List
from pydantic import BaseModel
from sqlmodel import Field, ARRAY, SQLModel, create_engine, Column, Float, JSON, BINARY, TIMESTAMP, text, UUID, FetchedValue, Interval, PrimaryKeyConstraint, UniqueConstraint

from datetime import datetime, timedelta
import uuid as uuid_pkg

# import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


from src.utils import get_password_hash, verify_password





def _newid():
    return uuid_pkg.uuid4()


def _isid(id):
    try:
        uuid_obj = uuid_pkg.UUID(id, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == id


class Base(SQLModel):
    id: uuid_pkg.UUID = Field(default=None, sa_type=UUID, 
        sa_column_kwargs={
            'primary_key': True,
            'index': True,
            'nullable': False,
            'server_default': text('gen_random_uuid()')
    })
    created_timestamp: datetime = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True), 
        sa_column_kwargs={
            'nullable': False,
            'server_default': text('CURRENT_TIMESTAMP')
    })
    updated_timestamp: datetime = Field(
        default=None,
        sa_type=TIMESTAMP(timezone=True), 
        sa_column_kwargs={
            'nullable': False,
            'server_default': text('CURRENT_TIMESTAMP'),
            'server_onupdate': FetchedValue()
    })

    def __repr__(self) -> str:
        return f'Base(id={str(self.id)!r}, create_date={self.create_date.isoformat()!r}, update_date={self.update_date.isoformat()!r})'



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
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    

class TaskBase(SQLModel):
    name: str
    description: str
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
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
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
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



class ViewBase(SQLModel):
    name: str
    filter: str
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
    ))


class View(Base, ViewBase, table=True):
    pass


class ViewCreate(ViewBase):
    pass


class ViewRead(Base, ViewBase):
    pass


class ViewUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter: Optional[str] = None
    doc: Optional[Dict] = None



class ResourceBase(SQLModel):
    name: str
    type: str
    availability: str
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
    ))


class Resource(Base, ResourceBase, table=True):
    pass


class ResourceCreate(ResourceBase):
    pass


class ResourceRead(Base, ResourceBase):
    pass


class ResourceUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str]
    availability: Optional[str]
    doc: Optional[Dict] = None


class WorklogBase(SQLModel):
    task_id: uuid_pkg.UUID = Field(nullable=False, foreign_key='task.id')
    name: str
    description: str = None
    timestamp: datetime = Field(nullable=False, sa_type=TIMESTAMP(timezone=True))
    duration: timedelta = Field(nullable=False, sa_type=Interval)
    doc: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
    ))


class Worklog(Base, WorklogBase, table=True):
    user_id: uuid_pkg.UUID = Field(default=None, foreign_key='user.id')


class WorklogCreate(WorklogBase):
    pass


class WorklogRead(Base, WorklogBase):
    user_id: uuid_pkg.UUID


class WorklogUpdate(SQLModel):
    task_id: Optional[uuid_pkg.UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration: Optional[timedelta] = None
    doc: Optional[Dict] = None


class BaselineTaskBase(SQLModel):
    duration: Optional[timedelta] = Field(default='P0D', nullable=False, sa_type=Interval)
    parent: Optional[uuid_pkg.UUID | None] = Field(nullable=True, foreign_key='task.id')
    # predecessors: Optional[Dict] = Field(default={}, sa_column=Column(
    #     JSON().with_variant(JSONB(), 'postgresql'), 
    #     nullable=False,
    #     server_default=text(''''{}'::jsonb''')
    # ))
    start: Optional[datetime | None]  = Field(nullable=True, sa_type=TIMESTAMP(timezone=True))
    finish: Optional[datetime | None]  = Field(nullable=True, sa_type=TIMESTAMP(timezone=True))
    auto_allocation: Optional[bool]  = True
    doc: Optional[Dict] = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
    ))


class BaselineTask(BaselineTaskBase, table=True):
    wbs: str = ''
    task_id: uuid_pkg.UUID = Field(nullable=False, foreign_key='task.id', index=True)
    baseline_id: uuid_pkg.UUID = Field(nullable=False, foreign_key='baseline.id', index=True)
    validation: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
    ))

    __table_args__ = (
        PrimaryKeyConstraint('baseline_id', 'task_id', name='bt_pk'),
    )


class BaselineTaskCreate(BaselineTaskBase):
    pass

    
class BaselineTaskRead(BaselineTaskBase):
    baseline_id: uuid_pkg.UUID
    task_id: uuid_pkg.UUID
    validation: Dict


class BaselineTaskUpdate(SQLModel):
    duration: Optional[timedelta] = None
    parent: Optional[uuid_pkg.UUID] = None
    # predecessors: Optional[Dict] = None
    start: Optional[datetime] = None
    finish: Optional[datetime] = None
    auto_allocation: Optional[bool] = None
    doc: Optional[Dict] = None


class BaselineTaskPredecessorBase(SQLModel):
    type: str


class BaselineTaskPredecessor(BaselineTaskPredecessorBase, table=True):
    task_id: uuid_pkg.UUID = Field(nullable=False, foreign_key='task.id', index=True)
    baseline_id: uuid_pkg.UUID = Field(nullable=False, foreign_key='baseline.id', index=True)
    predecessor_id: uuid_pkg.UUID = Field(nullable=False, foreign_key='task.id')
    validation: Dict = Field(default={}, sa_column=Column(
        JSON().with_variant(JSONB(), 'postgresql'), 
        nullable=False,
        server_default=text(''''{}'::jsonb''')
    ))

    __table_args__ = (
        PrimaryKeyConstraint('baseline_id', 'task_id', 'predecessor_id', name='btp_pk'),
    )


class BaselineTaskPredecessorCreate(BaselineTaskPredecessorBase):
    pass

    
class BaselineTaskPredecessorRead(BaselineTaskPredecessorBase):
    baseline_id: uuid_pkg.UUID
    task_id: uuid_pkg.UUID
    predecessor_id: uuid_pkg.UUID
    validation: Dict


class BaselineTaskPredecessorUpdate(SQLModel):
    type: str




class Token(BaseModel):
    token_type: str = 'bearer'
    access_token: str = None


class TokenData(BaseModel):
    username: str | None = None

