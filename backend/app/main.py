from fastapi import FastAPI, WebSocket
import json, copy

# from src.TasksList import TasksList
from src.TasksListMessages import TasksListMessages
from src.tmpdata import demo_data



app = FastAPI()

# global_websocket = WebSocket()


@app.get("/health")
async def health() -> str:
    return 'OK'


@app.websocket("/taskslist")
async def websocket_taskslist(websocket: WebSocket):
    taskslist = TasksListMessages()
    taskslist.tasks_list.reinit_tasks(copy.deepcopy(demo_data))
    await websocket.accept()
    print('client connected to taskslist ws')
    while True:
        data = await websocket.receive_text()
        if taskslist.exec(json.loads(data)): continue
        await websocket.send_text(json.dumps(taskslist.tasks_list.tasks))
