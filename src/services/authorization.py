import logging
from datetime import timedelta, datetime
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt

from src.core.config import app_settings
from src.models.models import User
from src.tools.password import verify_password
from src.db.db import get_session
from src.schemas import auth as auth_schema

logging.getLogger('service_auth')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v1/authorization/token')


async def get_user(db: AsyncSession, username: str):
    statement = select(
        User
    ).where(
        User.username == username
    )
    results = await db.execute(statement=statement)
    return results.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        app_settings.secret_key,
        algorithm=app_settings.algorithm
    )
    return encoded_jwt


def get_credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )


def get_token_data(
        token: str,
        credentials_exception: HTTPException
) -> (auth_schema.TokenData, str):
    try:
        payload = jwt.decode(
            token,
            app_settings.secret_key,
            algorithms=[app_settings.algorithm]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        return auth_schema.TokenData(username=username)
    except JWTError:
        logging.exception('Exception at get_current func for token %s', token)
        raise credentials_exception


async def get_user_by_token_data(
        token_data: auth_schema.TokenData,
        credentials_exception: HTTPException,
        db: AsyncSession = Depends(get_session)
) -> User:
    user = await get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user(db: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = get_credentials_exception()
    token_data = get_token_data(
        token=token,
        credentials_exception=credentials_exception
    )
    user = await get_user_by_token_data(
        token_data=token_data,
        credentials_exception=credentials_exception,
        db=db
    )
    if user.reset_token and user.reset_token == token:
        raise credentials_exception
    return user


async def get_current_user_for_reset_password(
        db: AsyncSession = Depends(get_session),
        token: str = Depends(oauth2_scheme)
):
    credentials_exception = get_credentials_exception()
    reset_token_data = get_token_data(
        token=token,
        credentials_exception=credentials_exception
    )
    user = await get_user_by_token_data(
        token_data=reset_token_data,
        credentials_exception=credentials_exception,
        db=db
    )
    if user.reset_token != token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Available only for reset password with reset token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user


async def get_token(db: AsyncSession, username: str, password: str):
    user: Union[User, bool] = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(minutes=app_settings.token_expire_minutes)
    token = create_access_token(
        data={'sub': user.username},
        expire_delta=access_token_expires
    )
    return {'access_token': token, 'token_type': 'bearer'}
