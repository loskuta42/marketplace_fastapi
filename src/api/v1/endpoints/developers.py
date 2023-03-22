import logging.config
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.models.models import User
from src.schemas import pub_dev as pub_dev_schema
from src.services.authorization import get_current_user
from src.tools.developers import check_developer_by_id, check_duplicating_developer
from src.tools.users import check_staff_permission
from src.services.base import developer_crud

logger = logging.getLogger('developers')

router = APIRouter()


@router.post(
    '/',
    response_model=pub_dev_schema.PubDevInDB,
    status_code=status.HTTP_201_CREATED,
    description='Create new developer.'
)
async def create_developer(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        developer_in: pub_dev_schema.PubDevCreate
) -> Any:
    """
    Create new developer.
    """
    check_staff_permission(current_user)
    developer_obj = await developer_crud.get_by_name(db=db, obj_in=developer_in)
    if developer_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='developer with this name exists.'
        )
    developer = await developer_crud.create(db=db, obj_in=developer_in)
    logger.info('Create developer - %s, by user - %s,', developer.name, current_user.username)
    return developer


@router.get(
    '/',
    response_model=pub_dev_schema.PubDevMulti,
    status_code=status.HTTP_200_OK,
    description='Get list og developers.'
)
async def get_developers(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 50
) -> Any:
    """
    Retrieve developers.
    """
    developers = await developer_crud.get_multi(db=db, skip=skip, limit=limit)
    logger.info('Return list of developers to user with id %s', current_user.id)
    return developers


@router.get(
    '/{developer_id}',
    response_model=pub_dev_schema.PubDevInDB,
    status_code=status.HTTP_200_OK,
    description='Get developer info by id.'
)
async def get_developer(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        developer_id: str
) -> Any:
    """
    Get developer by id.
    """
    developer_obj = await check_developer_by_id(db=db, developer_id=developer_id)
    logger.info('Return developer info with id %s to user with id %s', developer_obj.id, current_user.id)
    return developer_obj


@router.patch(
    '/{developer_id}',
    response_model=pub_dev_schema.PubDevInDB,
    status_code=status.HTTP_200_OK,
    description='Partial update developer info.'
)
async def patch_developer(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        developer_id: str,
        developer_in: pub_dev_schema.PubDevUpdate
) -> Any:
    """
    Patch developer info.
    """
    check_staff_permission(cur_user_obj=current_user)
    developer_obj = await check_developer_by_id(db=db, developer_id=developer_id)
    developer_name_before = developer_obj.name
    await check_duplicating_developer(developer_in=developer_in, db=db, developer_obj=developer_obj)
    developer_obj_patched = await developer_crud.patch(
        db=db,
        obj_in=developer_in,
        obj=developer_obj
    )
    logger.info(
        'Partial update developer %s (new name is %s) info.',
        developer_name_before,
        developer_obj_patched.name if developer_name_before != developer_obj_patched.name else developer_name_before
    )
    return developer_obj_patched


@router.delete(
    '/{developer_id}',
    description='Delete developer.',
    responses={
        status.HTTP_200_OK: {
            'model': pub_dev_schema.PubDevDelete,
            'description': 'Delete developer.'
        }
    }
)
async def delete_developer(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        developer_id: str
) -> Any:
    """
    Delete developer.
    """
    check_staff_permission(cur_user_obj=current_user)
    developer_obj = await check_developer_by_id(db=db, developer_id=developer_id)
    await developer_crud.delete(db=db, obj=developer_obj)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'info': f'Developer {developer_id} has been deleted.'
        }
    )
