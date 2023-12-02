from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import copy
import logging

from sqlalchemy import insert, select, func
from sqlalchemy.orm import sessionmaker

# from src.TasksList import TasksList
from src.TasksListMessages import TasksListMessages
from src.tmpdata import demo_data
from src.database import engine
from src.models import Base, User, Task, Baseline, UserView, _newid


FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()

Base.metadata.create_all(engine, checkfirst=True)

def init_db():
    Session = sessionmaker(engine)
    with Session() as session:
        result, = session.query(func.count(User.id)).one()
        if result == 0:
            for i in range(10):
                session.execute(insert(User).values(id=_newid(), name=f'User {i}'))
            session.commit()

init_db()

app = FastAPI()

# global_websocket = WebSocket()


@app.get("/health")
async def health() -> str:
    return 'OK'


@app.websocket("/taskslist")
async def websocket_taskslist(websocket: WebSocket):
    taskslist = TasksListMessages(engine)
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
        except WebSocketDisconnect:
            return
        result = taskslist.exec(data)
        await websocket.send_json(result)
