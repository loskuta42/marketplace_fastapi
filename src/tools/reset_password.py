import logging.config
from datetime import timedelta
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from fastapi import HTTPException, status

from src.core.config import app_settings
from src.services.authorization import create_access_token, get_user
from src.schemas import users as users_schema
from src.services.base import user_crud
from src.models.models import User


logger = logging.getLogger('reset_password')


async def get_reset_token(db: AsyncSession, user_in: users_schema.ForgetPasswordRequestBody):
    user: Union[User, bool] = await user_crud.get_by_email(db=db, obj_in=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_UNAUTHORIZED,
            detail='User with this email not exists.',
        )
    reset_token_expires = timedelta(minutes=app_settings.reset_token_expire_minutes)
    token = create_access_token(
        data={'sub': user.username},
        expire_delta=reset_token_expires
    )
    return token


async def get_user_by_reset_token(db: AsyncSession, reset_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Page not found',
    )
    try:
        payload = jwt.decode(
            reset_token,
            app_settings.secret_key,
            algorithms=[app_settings.algorithm]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        logger.exception('Exception at get_user_by_reset_token func for token %s', reset_token)
        raise credentials_exception
    user = await get_user(db=db, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_auth_token_for_reset_password(user: User):
    reset_password_auth_token_expires = timedelta(minutes=app_settings.reset_password_auth_token_expire_minutes)
    token = create_access_token(
        data={'sub': user.username},
        expire_delta=reset_password_auth_token_expires
    )
    return {'access_token': token, 'token_type': 'bearer'}
