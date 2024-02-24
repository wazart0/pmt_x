from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import Annotated
import base64

from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, and_, or_


import src.api_models as api
import src.db_models as db
from src.database import engine


# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "fakehashedpass",
#         "disabled": False,
#     },
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "email": "alice@example.com",
#         "hashed_password": "fakehashedpass",
#         "disabled": True,
#     },
# }



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password: str):
    return "fakehashed_" + password
    

def get_user_by_name(name: str):
    with Session(engine) as session:
        user = session.query(db.User).filter(db.User.name == name).first()
        return user
    

def get_user_by_id(id: str):
    with Session(engine) as session:
        user = session.query(db.User).filter(db.User.id == id).first()
        return user


def decode_token_and_retrieve_user(token):
    # This doesn't provide any security at all
    # TODO: Check the next version
    try:
        user_id = base64.b64decode(bytes(token, 'utf-8')).decode('utf-8')
    except:
        return None
    return get_user_by_id(user_id)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = decode_token_and_retrieve_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(
    user: Annotated[api.User, Depends(get_current_user)]
):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return user




def generate_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user_by_name(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    ### TODO: implement password validation
    # hashed_password = fake_hash_password(form_data.password)
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = base64.b64encode(bytes(str(user.id), 'utf-8'))
    return {"access_token": token, "token_type": "bearer"}
