from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.services.base import user_crud
from src.models.models import User
from src.schemas import user as user_schema


async def check_user_by_id(db: AsyncSession, user_id: str) -> User:
    user_obj = await user_crud.get_by_id(db=db, user_id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail='User not found.'
        )
    return user_obj


def check_staff_or_owner_permission(cur_user_obj: User, owner_id: str) -> None:
    if not (cur_user_obj.id == owner_id or cur_user_obj.is_staff):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not permission for this action.'
        )


def check_staff_permission(cur_user_obj: User) -> None:
    if not cur_user_obj.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not permission for this action.'
        )


async def check_for_duplicating_user(
        user_in: user_schema.UserUpgrade,
        db: AsyncSession,
        user_obj: User
):
    user_in_data = jsonable_encoder(user_in, exclude_none=True)
    if 'email' in user_in_data:
        user = await user_crud.get_by_email(db=db, obj_in=user_in)
        if user and user_obj.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists'
            )
    if 'username' in user_in_data:
        user = await user_crud.get_by_username(db=db, obj_in=user_in)
        if user and user_obj.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this username already exists'
            )
