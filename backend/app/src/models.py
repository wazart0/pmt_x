# from typing import List
# from typing import Optionalfrom 
# from typing import Dict
from uuid import UUID
import uuid
from typing import Sequence
from datetime import datetime

from sqlalchemy import JSON, inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, DeclarativeBase



class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, insert_default=uuid.uuid4())
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    update_date: Mapped[datetime] = mapped_column(insert_default=func.now(), onupdate=func.now())
    type_annotation_map = {
            Sequence[str]: JSON().with_variant(JSONB(), 'postgresql'),
        }
    
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class Task(Base):
    __tablename__ = 'task'

    # id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(511))
    doc: Mapped[Sequence[str]]
    
    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}, doc={self.doc!r})'
    
    def to_dict(self):
        return { str(self.id): { 
                'name': self.name,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat(),
                'doc': self.doc
            } }



class Baseline(Base):
    __tablename__ = 'baseline'

    # id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(511))
    doc: Mapped[Sequence[str]]
    
    def __repr__(self) -> str:
        return f'Baseline(id={self.id!r}, name={self.name!r}, doc={self.doc!r})'
    
    def to_dict(self):
        return { str(self.id): { 
                'name': self.name,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat(),
                'doc': self.doc
            } }



class UserView(Base):
    __tablename__ = 'user_view'

    # id: Mapped[UUID] = mapped_column(primary_key=True, insert_default=uuid.uuid4())
    user_id: Mapped[UUID]
    name: Mapped[str] = mapped_column(String(511))
    doc: Mapped[Sequence[str]]
    
    def __repr__(self) -> str:
        return f'Baseline(id={self.id!r}, name={self.name!r}, doc={self.doc!r})'
    
    def to_dict(self):
        return { str(self.id): { 
                'name': self.name,
                'create_date': self.create_date.isoformat(),
                'update_date': self.update_date.isoformat(),
                'doc': self.doc
            } }
    