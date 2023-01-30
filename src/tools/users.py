from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.services.base import user_crud
from src.models.models import User


async def check_user_by_id(db: AsyncSession, user_id: str) -> User:
    user_obj = await user_crud.get_by_id(db=db, user_id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail='User not found.'
        )
    return user_obj


def check_staff_or_author_permission(cur_user_obj: User, author_id: str) -> None:
    if not (cur_user_obj.id == author_id or cur_user_obj.is_staff):
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
