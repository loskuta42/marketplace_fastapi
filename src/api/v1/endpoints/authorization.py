import logging.config
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.schemas import auth as auth_schema, users as user_schema
from src.services.authorization import get_token

logger = logging.getLogger()

router = APIRouter()


@router.post(
    '/token',
    response_model=auth_schema.TokenUI,
    description='Authorization form for Swagger UI.'
)
async def login_ui_for_access_token(
        *,
        db: AsyncSession = Depends(get_session),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Endpoint for login in swagger UI."""
    access_token = await get_token(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    logger.info(f'Send token for {form_data.username} in Swagger UI')
    return access_token


@router.post(
    '/auth',
    response_model=auth_schema.Token,
    description='Get token for user.'
)
async def get_token_for_user(
        *,
        db: AsyncSession = Depends(get_session),
        obj_in: user_schema.UserAuth
) -> Any:
    """Get token for user."""
    username, password = obj_in.username, obj_in.password
    access_token = await get_token(
        db=db,
        username=username,
        password=password
    )
    logger.info('Send token for %s', username)
    return access_token
