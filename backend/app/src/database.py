# from sqlalchemy import create_engine
from sqlmodel import create_engine
from src.config import config
from src.logger import logger
import psycopg2

# load_dotenv()

# db_host = os.environ['POSTGRES_HOST']
# db_port = os.environ['POSTGRES_PORT']
# db_name = os.environ['POSTGRES_NAME']
# db_user = os.environ['POSTGRES_USER']
# db_pass = os.environ['POSTGRES_PASSWORD']
# pg_url = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}'


pg_url = f'postgresql+psycopg2://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_NAME']}'

engine = create_engine(pg_url, echo=True)


def is_db_up():
    try:
        conn = psycopg2.connect(
            database="postgres",
            user=config['POSTGRES_USER'],
            password=config['POSTGRES_PASSWORD'],
            host=config['POSTGRES_HOST'],
            port=config['POSTGRES_PORT']
        )
        conn.close()
        return True
    except:
        return False
