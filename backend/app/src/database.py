from sqlalchemy import create_engine
from .config import config

# load_dotenv()

# db_host = os.environ['POSTGRES_HOST']
# db_port = os.environ['POSTGRES_PORT']
# db_name = os.environ['POSTGRES_NAME']
# db_user = os.environ['POSTGRES_USER']
# db_pass = os.environ['POSTGRES_PASSWORD']
# pg_url = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}'


pg_url = f'postgresql+psycopg2://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_NAME']}'

engine = create_engine(pg_url)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)