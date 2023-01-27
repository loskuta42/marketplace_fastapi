import logging.config
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.schemas import user as user_schema
from src.services.base import user_crud
from src.services.authorization import get_current_user


logger = logging.getLogger('users')

router = APIRouter()


@router.post(
    '/',
    response_model=user_schema.UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    description='Create new user.'
)
async def create_user(
        *,
        db: AsyncSession = Depends(get_session),
        user_in: user_schema.UserRegister
) -> Any:
    """
    Create new user.
    """
    user_obj = await user_crud.get_by_username(db=db, obj_in=user_in)
    if user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this username exists.'
        )
    user = await user_crud.create(db=db, obj_in=user_in)
    logger.info('Create user - %s', user.username)
    return user


@router.get(
    '/{user_id}',
    response_model=user_schema.UserInDB,
    status_code=status.HTTP_200_OK,
    description='Get user info.'
)
async def get_user(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: user_schema.UserInDB = Depends(get_current_user),
        user_id: str
) -> Any:
    """
    Get user by id.
    """
    user_obj = await user_crud.get_by_id(db=db, user_id=user_id)
    if user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found.'
        )
    logger.info('Return user info with id %s to user with id %s', user_id, current_user.id)
    return user_obj

