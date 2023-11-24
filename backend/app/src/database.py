from sqlalchemy import create_engine
import os



db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_pass = os.environ['DB_PASS']

pg_url = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}'

engine = create_engine(pg_url)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)