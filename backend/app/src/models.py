# from typing import List
# from typing import Optionalfrom 
# from typing import Dict
from uuid import UUID
from typing import Sequence
from datetime import datetime

from sqlalchemy import JSON, inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, DeclarativeBase


def _newid():
    import uuid
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    type_annotation_map = {
            Sequence[str]: JSON().with_variant(JSONB(), 'postgresql'),
        }

    id: Mapped[UUID] = mapped_column(primary_key=True, insert_default=_newid())
    name: Mapped[str] = mapped_column(String(511))
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    update_date: Mapped[datetime] = mapped_column(insert_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}, create_date={self.name!r}, update_date={self.name!r})'
    
    def to_dict(self):
        return { 
                'id': str(self.id),
                'name': self.name,
                'doc': self.doc,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat()
            }



class User(Base):
    __tablename__ = 'user'



class Task(Base):
    __tablename__ = 'task'

    description: Mapped[str] = mapped_column(insert_default='')
    doc: Mapped[Sequence[str]] = mapped_column(insert_default={})
    
    def to_dict(self):
        return { 
                'id': str(self.id),
                'name': self.name,
                'description': self.description,
                'doc': self.doc,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat()
            }



class Baseline(Base):
    __tablename__ = 'baseline'

    description: Mapped[str] = mapped_column(insert_default='')
    tasks: Mapped[Sequence[str]] = mapped_column(insert_default={})
    doc: Mapped[Sequence[str]] = mapped_column(insert_default={})
    
    def to_dict(self):
        return { 
                'id': str(self.id),
                'name': self.name,
                'description': self.description,
                'doc': self.doc,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat()
            }



class UserView(Base):
    __tablename__ = 'user_view'

    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id))
    filter: Mapped[str] = mapped_column(insert_default='')
    doc: Mapped[Sequence[str]] = mapped_column(insert_default={})
    
    def to_dict(self):
        return { 
                'id': str(self.id),
                'name': self.name,
                'filter': self.filter,
                'doc': self.doc,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat()
            }
