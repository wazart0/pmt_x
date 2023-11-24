from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json, copy
import logging

# from src.TasksList import TasksList
from src.TasksListMessages import TasksListMessages
from src.tmpdata import demo_data
from src.database import engine
from src.models import Base, Task, Baseline, UserView


FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()


app = FastAPI()
Base.metadata.create_all(engine, checkfirst=True)

# global_websocket = WebSocket()


@app.get("/health")
async def health() -> str:
    return 'OK'


@app.websocket("/taskslist")
async def websocket_taskslist(websocket: WebSocket):
    taskslist = TasksListMessages(engine)
    # taskslist.tasks_list.reinit_tasks(copy.deepcopy(demo_data))
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            return
        result = taskslist.exec(json.loads(data))
        await websocket.send_text(json.dumps(result))
        # await websocket.send_text(json.dumps(taskslist.tasks_list.get_view()))
