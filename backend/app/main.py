from fastapi import FastAPI, WebSocket
import json

from src.TasksList import TasksList



app = FastAPI()

# global_websocket = WebSocket()


@app.get("/health")
async def health():
    return 'OK'


# @app.get("/data")
# async def data():
#     return taskslist.data


@app.websocket("/taskslist")
async def websocket_taskslist(websocket: WebSocket):
    taskslist = TasksList()
    await websocket.accept()
    print('client connected to taskslist ws')
    while True:
        data = await websocket.receive_text()
        data_json = json.loads(data)
        print(data_json)
        await websocket.send_text(json.dumps(taskslist.data))
