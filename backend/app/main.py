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
        result = taskslist.exec(json.loads(data))
        if result: websocket.send_text(json.dumps({'error': result}))
        await websocket.send_text(json.dumps({'data': taskslist.tasks_list.tasks}))
