from sqlalchemy_utils import database_exists, create_database

from sqlalchemy import insert, select, func
from sqlalchemy.orm import sessionmaker

from src.database import engine
from src.db_models import Base, User, Task, Baseline, UserView, _newid



def migrate():
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(engine, checkfirst=True)

    Session = sessionmaker(engine)
    with Session() as session:
        result, = session.query(func.count(User.id)).one()
        if result == 0:
            for i in range(10):
                session.execute(insert(User).values(id=_newid(), name=f'User {i}'))
            session.commit()
