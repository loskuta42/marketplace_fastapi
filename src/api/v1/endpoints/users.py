import logging.config
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import MessageSchema, MessageType

from src.db.db import get_session
from src.schemas import users as user_schema
from src.services.base import user_crud
from src.services.authorization import get_current_user
from src.models.models import User
from src.tools.users import (
    check_user_by_id,
    check_staff_or_owner_permission,
    check_staff_permission,
    check_for_duplicating_user,
    check_user_by_email
)
from src.tools.reset_password import (
    get_reset_token,
    get_user_by_reset_token,
    get_auth_token_for_reset_password,
    reset_password_for_user
)
from src.core.config import app_settings, mail_config

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
    '/',
    response_model=user_schema.UserMulti,
    status_code=status.HTTP_200_OK,
    description='List of users'
)
async def get_users(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100
) -> Any:
    """
    Retrieve users.
    """
    users = await user_crud.get_multi(db=db, skip=skip, limit=limit)
    logger.info('Return list of users to user with id %s', current_user.id)
    return users


@router.get(
    '/{user_id}',
    response_model=user_schema.UserInDB,
    status_code=status.HTTP_200_OK,
    description='Get user info.'
)
async def get_user(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        user_id: str
) -> Any:
    """
    Get user by id.
    """
    user_obj = await check_user_by_id(db=db, user_id=user_id)
    logger.info('Return user info with id %s to user with id %s', user_id, current_user.id)
    return user_obj


@router.patch(
    '/{user_id}',
    response_model=user_schema.UserInDB,
    status_code=status.HTTP_200_OK,
    description='Partial update user info.'
)
async def patch_user(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        user_id: str,
        user_in: user_schema.UserUpgrade
) -> Any:
    """
    Patch user info.
    """
    user_obj = await check_user_by_id(db=db, user_id=user_id)
    check_staff_permission(cur_user_obj=current_user)
    await check_for_duplicating_user(db=db, user_in=user_in, user_obj=user_obj)
    user_obj_patched = await user_crud.patch(
        db=db,
        user_obj=user_obj,
        user_in=user_in
    )
    logger.info(f'Partial update {user_obj.username} info.')
    return user_obj_patched


@router.delete(
    '/{user_id}',
    description='Delete user.',
    responses={
        status.HTTP_200_OK: {
            'model': user_schema.UserDelete,
            'description': 'Delete user.'
        }
    }
)
async def delete_user(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        user_id: str
) -> Any:
    """
    Delete user.
    """
    user_obj = await check_user_by_id(db=db, user_id=user_id)
    check_staff_permission(cur_user_obj=current_user)
    await user_crud.delete(db=db, user_obj=user_obj)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'info': f'User {user_id} has been deleted.'
        }
    )


@router.get(
    '/me/',
    response_model=user_schema.UserInDB,
    description='Get personal user info.'
)
async def get_personal_info(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Get personal current user info.
    """
    user_obj = await check_user_by_id(db=db, user_id=current_user.id)
    logger.info('Return personal user info to user with id %s', current_user.id)
    return user_obj


@router.patch(
    '/me/',
    response_model=user_schema.UserInDB,
    description='Patch personal user info'
)
async def patch_personal_info(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        user_in: user_schema.UserUpgrade
):
    """
    Get personal current user info.
    """
    await check_for_duplicating_user(db=db, user_in=user_in, user_obj=current_user)
    user_obj_patched = await user_crud.patch(
        db=db,
        user_obj=current_user,
        user_in=user_in
    )
    logger.info(f'Partial update {current_user.username} info.')
    return user_obj_patched


@router.post(
    '/forget-password/',
    response_model=user_schema.ForgetPasswordResponse,
    description='Send email for password reset'
)
async def forget_password(
        *,
        db: AsyncSession = Depends(get_session),
        user_in: user_schema.ForgetPasswordRequestBody
):
    """
    Send email for password reset.
    """
    from src.main import app, fast_mail
    user_obj = await check_user_by_email(db=db, user_in=user_in)
    reset_token = await get_reset_token(db=db, user_in=user_in)
    url = ('http://'+app_settings.project_host + ':' +
           str(app_settings.project_port) +
           app.url_path_for('confirm_reset_token', reset_token=reset_token))
    email_data = {
        'username': user_obj.username,
        'url': url
    }
    email = user_in.dict().get('email')
    message = MessageSchema(
        subject='Reset password',
        recipients=[email],
        template_body=email_data,
        subtype=MessageType.html
    )
    await fast_mail.send_message(message, template_name='email.html')
    return {'info': f'reset password email has been sent to {email}'}


@router.get(
    '/reset-password/{reset_token}',
    status_code=status.HTTP_200_OK,
    response_model=user_schema.ResetToken,
    description='Confirm reset token and return access token'
)
async def confirm_reset_token(
        *,
        db: AsyncSession = Depends(get_session),
        reset_token: str
):
    user = await get_user_by_reset_token(db=db, reset_token=reset_token)
    token = get_auth_token_for_reset_password(user)
    return token


@router.patch(
    '/reset-password/',
    response_model=user_schema.ResetPasswordResponse,
    description='Reset password for user'
)
async def reset_password(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        user_in: user_schema.ResetPassword
):
    user = await reset_password_for_user(db=db, user=current_user, user_in=user_in)
    logger.info('Password successfully reset for user - %s', user.username)
    return {'info': 'Password successfully reset.'}

# @router.patch(
#     '/change-password/',
#     response_model=user_schema
# )