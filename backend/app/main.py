from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated
import copy
import logging

# from src.TasksList import TasksList
from src.TasksListMessages import TasksListMessages
from src.tmpdata import demo_data
from src.database import engine
from src.migration import migrate
from src.authentication import generate_token, get_current_active_user
from src.api_models import User


FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()

migrate()

app = FastAPI()



@app.get("/health")
def health() -> str:
    return 'OK'


@app.post("/token")
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return generate_token(form_data)


@app.get("/user")
def user(
    user: Annotated[User, Depends(get_current_active_user)]
    ):
    return user


@app.websocket("/taskslist")
async def websocket_taskslist(
    user: Annotated[User, Depends(get_current_active_user)],
    websocket: WebSocket
    ):
    taskslist = TasksListMessages(engine)
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
        except WebSocketDisconnect:
            return
        result = taskslist.exec(data)
        await websocket.send_json(result)
