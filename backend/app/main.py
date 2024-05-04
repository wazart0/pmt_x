from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from typing import Annotated, List
import time

# from src.TasksList import TasksList
from src.TasksListMessages import TasksListMessages
from src.database import engine, is_db_up
from src.migration import migrate_database
from src.authentication import create_access_token, get_current_user, authenticate_user
from src.api_models import Token
from src.utils import get_password_hash
from src.error import error_details, Error
from src.logger import logger

import src.models as models
from src.models import User, UserCreate, UserRead, UserUpdate
from src.models import Task, TaskCreate, TaskRead, TaskUpdate
from src.models import Baseline, BaselineCreate, BaselineRead, BaselineUpdate
from src.models import View, ViewCreate, ViewRead, ViewUpdate
from src.models import Resource, ResourceCreate, ResourceRead, ResourceUpdate
from src.models import Worklog, WorklogCreate, WorklogRead, WorklogUpdate
from src.models import BaselineTask, BaselineTaskCreate, BaselineTaskRead, BaselineTaskUpdate
from src.models import BaselineTaskPredecessor, BaselineTaskPredecessorCreate, BaselineTaskPredecessorRead, BaselineTaskPredecessorUpdate



@asynccontextmanager
async def lifespan(app: FastAPI):
    while not is_db_up():
        logger.error("Database is not available, retrying...")
        time.sleep(5)
    migrate_database()

    yield

    # Code at the end of the lifespan context manager will be executed after the app is shut down

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/health')
def health() -> str:
    return 'ok'


@app.post('/token')
def create_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
    with Session(engine) as session:
        user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_details(Error.CREATE_TOKEN, None),
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return Token(token_type='bearer', access_token=create_access_token(data={'sub': str(user.id)}))


@app.post('/user')
def create_user(user: UserCreate) -> UserRead:
    with Session(engine) as session:
        username = session.exec(select(User.username).where(User.username == user.username)).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_details(Error.CREATE_USER, None, username)
            )
        user.password = get_password_hash(user.password)
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.patch('/user')
def patch_user(
        db_user: Annotated[User, Depends(get_current_user)],
        user: UserUpdate
    ) -> UserRead:
    with Session(engine) as session:
        if user.username:
            username = session.exec(select(User.username).where(User.username == user.username)).first()
            if username and username != db_user.username:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=error_details(Error.PATCH_USER, db_user.id, username)
                )
        user_data = user.model_dump(exclude_unset=True)
        if 'password' in user_data:
            user_data['password'] = get_password_hash(user_data['password'])
        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.get('/user')
def get_user(db_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return db_user


@app.get('/users')
def get_users(
        db_user: Annotated[User, Depends(get_current_user)]
    ) -> List[UserRead]:
    with Session(engine) as session:
        db_users = session.exec(select(User)).all()
        return db_users



def create_object(Model, object, user_id, access_scope = None):
    with Session(engine) as session:
        db_object = Model.model_validate(object)
        if hasattr(db_object, 'user_id'):
            db_object.user_id = user_id
        session.add(db_object)
        try:
            session.commit()
        except IntegrityError as e:
            logger.info(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_details(Error.CREATE_OBJECT, user_id))
        session.refresh(db_object)
        return db_object


def patch_object(Model, id, object, user_id, access_scope = None):
    if not models._isid(id):
        raise HTTPException(status_code=404, detail=error_details(Error.PATCH_OBJECT_1, user_id, id))
    object_data = object.model_dump(exclude_unset=True)
    with Session(engine) as session:
        db_object = session.get(Model, id)
        if not db_object:
            raise HTTPException(status_code=404, detail=error_details(Error.PATCH_OBJECT_2, user_id, id))
        db_object.sqlmodel_update(object_data)
        try:
            session.commit()
        except IntegrityError as e:
            logger.info(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_details(Error.PATCH_OBJECT_3, user_id))
        session.refresh(db_object)
        return db_object


def get_object(Model, id, user_id, access_scope = None):
    if not models._isid(id):
        raise HTTPException(status_code=404, detail=error_details(Error.GET_OBJECT_1, user_id, id))
    with Session(engine) as session:
        db_object = session.get(Model, id)
        if not db_object:
            raise HTTPException(status_code=404, detail=error_details(Error.GET_OBJECT_2, user_id, id))
        return db_object


def get_objects(Model: object, order_by: str, desc: bool, user_id, access_scope = None):
    if not hasattr(Model, order_by):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=error_details(Error.GET_OBJECTS, user_id, order_by))
    with Session(engine) as session:
        statement = select(Model).order_by(getattr(Model, order_by).desc()) \
            if desc else select(Model).order_by(getattr(Model, order_by).asc())
        db_objects = session.exec(statement).all()
        return db_objects



@app.post('/sharespace/task')
def create_task(
        db_user: Annotated[User, Depends(get_current_user)],
        task: TaskCreate
    ) -> TaskRead:
    return create_object(Task, task, db_user.id)


@app.patch('/sharespace/task/{id}')
def patch_task(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str,
        task: TaskUpdate
    ) -> TaskRead:
    return patch_object(Task, id, task, db_user.id)


@app.get('/sharespace/task/{id}')
def get_task(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str
    ) -> TaskRead:
    return get_object(Task, id, db_user.id)


@app.get('/sharespace/tasks')
def get_tasks(
        db_user: Annotated[User, Depends(get_current_user)],
        order_by: str = 'updated_timestamp',
        desc: bool = False
    ) -> List[TaskRead]:
    return get_objects(Task, order_by, desc, db_user.id)


@app.post('/sharespace/baseline')
def create_baseline(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline: BaselineCreate
    ) -> BaselineRead:
    return create_object(Baseline, baseline, db_user.id)


@app.patch('/sharespace/baseline/{id}')
def patch_baseline(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str,
        baseline: BaselineUpdate
    ) -> BaselineRead:
    return patch_object(Baseline, id, baseline, db_user.id)


@app.get('/sharespace/baseline/{id}')
def get_baseline(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str
    ) -> BaselineRead:
    return get_object(Baseline, id, db_user.id)


@app.get('/sharespace/baselines')
def get_baselines(
        db_user: Annotated[User, Depends(get_current_user)],
        order_by: str = 'updated_timestamp',
        desc: bool = False
    ) -> List[BaselineRead]:
    return get_objects(Baseline, order_by, desc, db_user.id)


@app.post('/sharespace/view')
def create_view(
        db_user: Annotated[User, Depends(get_current_user)],
        view: ViewCreate
    ) -> ViewRead:
    return create_object(View, view, db_user.id)


@app.patch('/sharespace/view/{id}')
def patch_view(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str,
        view: ViewUpdate
    ) -> ViewRead:
    return patch_object(View, id, view, db_user.id)


@app.get('/sharespace/view/{id}')
def get_view(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str
    ) -> ViewRead:
    return get_object(View, id, db_user.id)


@app.get('/sharespace/views')
def get_views(
        db_user: Annotated[User, Depends(get_current_user)],
        order_by: str = 'updated_timestamp',
        desc: bool = False
    ) -> List[ViewRead]:
    return get_objects(View, order_by, desc, db_user.id)


@app.post('/sharespace/resource')
def create_resource(
        db_user: Annotated[User, Depends(get_current_user)],
        resource: ResourceCreate
    ) -> ResourceRead:
    return create_object(Resource, resource, db_user.id)


@app.patch('/sharespace/resource/{id}')
def patch_resource(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str,
        resource: ResourceUpdate
    ) -> ResourceRead:
    return patch_object(Resource, id, resource, db_user.id)


@app.get('/sharespace/resource/{id}')
def get_resource(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str
    ) -> ResourceRead:
    return get_object(Resource, id, db_user.id)


@app.get('/sharespace/resources')
def get_resources(
        db_user: Annotated[User, Depends(get_current_user)],
        order_by: str = 'updated_timestamp',
        desc: bool = True
    ) -> List[ResourceRead]:
    return get_objects(Resource, order_by, desc, db_user.id)


@app.post('/sharespace/worklog')
def create_worklog(
        db_user: Annotated[User, Depends(get_current_user)],
        worklog: WorklogCreate
    ) -> WorklogRead:
    return create_object(Worklog, worklog, db_user.id)


@app.patch('/sharespace/worklog/{id}')
def patch_worklog(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str,
        worklog: WorklogUpdate
    ) -> WorklogRead:
    return patch_object(Worklog, id, worklog, db_user.id)


@app.get('/sharespace/worklog/{id}')
def get_worklog(
        db_user: Annotated[User, Depends(get_current_user)],
        id: str
    ) -> WorklogRead:
    return get_object(Worklog, id, db_user.id)


@app.get('/sharespace/worklogs')
def get_worklogs(
        db_user: Annotated[User, Depends(get_current_user)],
        order_by: str = 'updated_timestamp',
        desc: bool = True
    ) -> List[WorklogRead]:
    return get_objects(Worklog, order_by, desc, db_user.id)


@app.post('/sharespace/baseline/{baseline_id}/task/{task_id}')
def create_baseline_task(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_task: BaselineTaskCreate,
        baseline_id: str,
        task_id: str
    ) -> BaselineTaskRead:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.CREATE_BASELINE_TASK_1, db_user.id, baseline_id))
    if not models._isid(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.CREATE_BASELINE_TASK_2, db_user.id, task_id))

    with Session(engine) as session:
        db_object = BaselineTask.model_validate(baseline_task, update={
            'baseline_id': baseline_id,
            'task_id': task_id
        })
        session.add(db_object)
        try:
            session.commit()
        except IntegrityError as e:
            logger.info(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_details(Error.CREATE_BASELINE_TASK_3, db_user.id, (baseline_id, task_id)))
        session.refresh(db_object)
        return db_object


@app.patch('/sharespace/baseline/{baseline_id}/task/{task_id}')
def patch_baseline_task(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_task: BaselineTaskUpdate,
        baseline_id: str,
        task_id: str
    ) -> BaselineTaskRead:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.PATCH_BASELINE_TASK_1, db_user.id, baseline_id))
    if not models._isid(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.PATCH_BASELINE_TASK_2, db_user.id, task_id))

    object_data = baseline_task.model_dump(exclude_unset=True)
    with Session(engine) as session:
        db_object = session.get(BaselineTask, (baseline_id, task_id))
        if not db_object:
            raise HTTPException(status_code=404, detail=error_details(Error.PATCH_BASELINE_TASK_3, db_user.id, (baseline_id, task_id)))
        db_object.sqlmodel_update(object_data)
        try:
            session.commit()
        except IntegrityError as e:
            logger.info(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_details(Error.PATCH_BASELINE_TASK_4, db_user.id, (baseline_id, task_id)))
        session.refresh(db_object)
        return db_object


@app.get('/sharespace/baseline/{baseline_id}/task/{task_id}')
def get_baseline_task(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_id: str,
        task_id: str
    ) -> BaselineTaskRead:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.GET_BASELINE_TASK_1, db_user.id, baseline_id))
    if not models._isid(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.GET_BASELINE_TASK_2, db_user.id, task_id))

    with Session(engine) as session:
        db_object = session.get(BaselineTask, (baseline_id, task_id))
        if not db_object:
            raise HTTPException(status_code=404, detail=error_details(Error.GET_BASELINE_TASK_3, db_user.id, (baseline_id, task_id)))
        return db_object


@app.get('/sharespace/baseline/{baseline_id}/tasks')
def get_baseline_tasks(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_id: str
    ) -> List[BaselineTaskRead]:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.GET_BASELINE_TASKS_1, db_user.id, baseline_id))

    with Session(engine) as session:
        statement = select(BaselineTask).filter_by(BaselineTask.baseline_id == baseline_id)
        db_objects = session.exec(statement).all()
        return db_objects


@app.post('/sharespace/baseline/{baseline_id}/task/{task_id}/predecessor/{predecessor_id}')
def create_baseline_task_predecessor(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_task: BaselineTaskPredecessorCreate,
        baseline_id: str,
        task_id: str,
        predecessor_id: str
    ) -> BaselineTaskPredecessorRead:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.CREATE_BASELINE_TASK_PREDECESSOR_1, db_user.id, baseline_id))
    if not models._isid(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.CREATE_BASELINE_TASK_PREDECESSOR_2, db_user.id, task_id))
    if not models._isid(predecessor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.CREATE_BASELINE_TASK_PREDECESSOR_3, db_user.id, predecessor_id))

    with Session(engine) as session:
        db_object = BaselineTaskPredecessor.model_validate(baseline_task, update={
            'baseline_id': baseline_id,
            'task_id': task_id,
            'predecessor_id': predecessor_id
        })
        session.add(db_object)
        try:
            session.commit()
        except IntegrityError as e:
            logger.info(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_details(Error.CREATE_BASELINE_TASK_PREDECESSOR_4, db_user.id, (baseline_id, task_id, predecessor_id)))
        session.refresh(db_object)
        return db_object


@app.delete('/sharespace/baseline/{baseline_id}/task/{task_id}/predecessor/{predecessor_id}')
def delete_baseline_task_predecessor(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_id: str,
        task_id: str,
        predecessor_id: str
    ) -> str:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.DELETE_BASELINE_TASK_PREDECESSOR_1, db_user.id, baseline_id))
    if not models._isid(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.DELETE_BASELINE_TASK_PREDECESSOR_2, db_user.id, task_id))
    if not models._isid(predecessor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details(Error.DELETE_BASELINE_TASK_PREDECESSOR_3, db_user.id, predecessor_id))

    with Session(engine) as session:
        db_object = session.get(BaselineTaskPredecessor, (baseline_id, task_id, predecessor_id))
        if not db_object:
            raise HTTPException(status_code=404, detail=error_details(Error.DELETE_BASELINE_TASK_PREDECESSOR_4, db_user.id, (baseline_id, task_id)))
        session.delete(db_object)
        try:
            session.commit()
        except IntegrityError as e:
            logger.info(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_details(Error.DELETE_BASELINE_TASK_PREDECESSOR_5, db_user.id, (baseline_id, task_id, predecessor_id)))
        return 'ok'


@app.get('/sharespace/baseline/{baseline_id}/predecessors')
def get_baseline_predecessors(
        db_user: Annotated[User, Depends(get_current_user)],
        baseline_id: str
    ) -> List[BaselineTaskPredecessorRead]:
    if not models._isid(baseline_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error_details(Error.GET_BASELINE_PREDECESSORS_1, db_user.id, baseline_id))

    with Session(engine) as session:
        statement = select(BaselineTaskPredecessor).filter_by(BaselineTaskPredecessor.baseline_id == baseline_id)
        db_objects = session.exec(statement).all()
        return db_objects






@app.websocket('/taskslist')
async def websocket_taskslist(
        db_user: Annotated[UserRead, Depends(get_current_user)],
        websocket: WebSocket
    ):
    taskslist = TasksListMessages(engine)
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
        except WebSocketDisconnect as e:
            logger.info(e)
            return
        result = taskslist.exec(data)
        await websocket.send_json(result)
