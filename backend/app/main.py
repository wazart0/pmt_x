from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import Session, select

from typing import Annotated, List
import copy
import logging

# from src.TasksList import TasksList
from src.TasksListMessages import TasksListMessages
from src.tmpdata import demo_data
from src.database import engine
from src.migration import migrate_database
from src.authentication import create_access_token, get_current_user, authenticate_user
from src.api_models import Token
from src.utils import get_password_hash
from src.models import UserRead, User, UserBase, UserCreate, Task, TaskCreate, TaskRead




FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()


app = FastAPI()


@app.on_event("startup")
def on_startup():
    migrate_database()


@app.get("/health")
def health() -> str:
    return 'OK'


@app.post("/token")
def token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
    with Session(engine) as session:
        user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(token_type="bearer", access_token=create_access_token(data={"sub": str(user.id)}))


@app.post("/user")
def create_user(user: UserCreate) -> UserRead:
    with Session(engine) as session:
        username = session.exec(select(User.username).where(User.username == user.username)).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Username already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.get("/user")
def get_user(user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return user


@app.get("/users")
def users(
        user: Annotated[User, Depends(get_current_user)]
    ) -> List[UserRead]:
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users


@app.post('/task')
def create_task(
        user: Annotated[User, Depends(get_current_user)],
        task: TaskCreate
    ) -> TaskRead:
    with Session(engine) as session:
        db_task = Task.model_validate(task)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task



@app.websocket("/taskslist")
async def websocket_taskslist(
        user: Annotated[UserRead, Depends(get_current_user)],
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
