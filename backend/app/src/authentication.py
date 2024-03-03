from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt
from typing import Annotated
import base64

# from sqlalchemy.orm import Session
# from sqlalchemy import insert, select, update, and_, or_
from sqlmodel import Session, select

from datetime import datetime, timedelta, timezone

# import src.api_models as api
# import src.db_models as db
from src.database import engine
from src.utils import get_password_hash, verify_password
from src.models import User, Token, TokenData
from src.config import config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(session, username: str, password: str):
    user = session.exec(select(User.id, User.username, User.password).where(User.username == username)).first()
    if not user:
        return False
    if not verify_password(password, user.password):   # TODO: implement passwords
        return False
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config['BE_JWT_SECRET_KEY'], algorithms=[config['BE_JWT_ALGORITHM']])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    with Session(engine) as session:
        # user = session.exec(select(User).where(User.username == username)).first()
        user = session.get(User, id)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(config['BE_JWT_TOKEN_EXPIRE_MINUTES']))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config['BE_JWT_SECRET_KEY'], algorithm=config['BE_JWT_ALGORITHM'])
