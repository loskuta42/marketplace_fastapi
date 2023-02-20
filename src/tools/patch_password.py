import logging.config
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.core.config import app_settings
from src.services.authorization import create_access_token, get_user
from src.schemas import users as users_schema
from src.services.base import user_crud
from src.models.models import User
from src.tools.password import get_password_hash, verify_password

logger = logging.getLogger('reset_password')


async def get_reset_code(db: AsyncSession, user_in: users_schema.ForgetPasswordRequestBody):
    user: User | bool = await user_crud.get_by_email(db=db, obj_in=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_UNAUTHORIZED,
            detail='User with this email not exists.',
        )
    reset_code_expires = timedelta(minutes=app_settings.reset_token_expire_minutes)
    reset_code = create_access_token(
        data={'sub': user.username},
        expire_delta=reset_code_expires
    )
    return reset_code


async def get_user_by_reset_code(db: AsyncSession, reset_code: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Page not found',
    )
    try:
        payload = jwt.decode(
            reset_code,
            app_settings.secret_key,
            algorithms=[app_settings.algorithm]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        logger.exception('Exception at get_user_by_reset_token func for token %s', reset_code)
        raise credentials_exception
    user = await get_user(db=db, username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_reset_token(db: AsyncSession, user: User):
    reset_password_auth_token_expires = timedelta(minutes=app_settings.reset_password_auth_token_expire_minutes)
    token = create_access_token(
        data={'sub': user.username},
        expire_delta=reset_password_auth_token_expires
    )
    user.reset_token = token
    db.add(user)
    await db.commit()
    return {'access_token': token, 'token_type': 'bearer'}


async def reset_password_for_user(
        db: AsyncSession,
        user: User,
        user_in: users_schema.ResetPassword | users_schema.ChangePassword
) -> User:
    new_password = jsonable_encoder(user_in)['new_password']
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password_for_user(db: AsyncSession, user: User, user_in: users_schema.ChangePassword) -> Any:
    old_password = jsonable_encoder(user_in)['old_password']
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Old password are incorrect.',
        )
    user = await reset_password_for_user(db=db, user=user, user_in=user_in)
    return user
