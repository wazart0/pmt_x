from sqlalchemy_utils import database_exists, create_database
from sqlmodel import SQLModel, Session, text

from sqlalchemy import func

from src.database import engine
from src.models import Base, User
from src.utils import get_password_hash



def migrate_database():
    if not database_exists(engine.url):
        create_database(engine.url)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        session.exec(text('''
            CREATE OR REPLACE FUNCTION update_timestamp() RETURNS TRIGGER 
            LANGUAGE plpgsql AS
            $$
            BEGIN
                NEW.updated_timestamp = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$;
            '''))

        for table_name in SQLModel.metadata.tables:
            session.exec(text(f'''
                CREATE OR REPLACE TRIGGER tg_update_timestamp
                    BEFORE UPDATE ON "{table_name}"
                    FOR EACH ROW
                    WHEN (OLD.* IS DISTINCT FROM NEW.*)
                    EXECUTE FUNCTION update_timestamp();
            '''))

        result, = session.query(func.count(User.id)).one()
        if result == 0:
            for i in range(10):
                session.add(User(name=f'User {i}', username=f'user{i}', password=get_password_hash(f'pass{i}')))
        
        session.commit()
