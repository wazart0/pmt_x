from sqlalchemy_utils import database_exists, create_database
from sqlmodel import SQLModel, Session

from sqlalchemy import func

from src.database import engine
from src.models import Base, User, Task, Baseline, UserView
from src.utils import get_password_hash



def migrate_database():
    if not database_exists(engine.url):
        create_database(engine.url)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        result, = session.query(func.count(User.id)).one()
        if result == 0:
            for i in range(10):
                session.add(User(name=f'User {i}', username=f'user{i}', password=get_password_hash(f'pass{i}')))
            session.commit()
