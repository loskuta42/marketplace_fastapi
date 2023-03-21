import logging.config
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.models.models import User
from src.schemas import pub_dev as pub_dev_schema
from src.services.authorization import get_current_user
from src.tools.publishers import check_publisher_by_id, check_duplicating_publisher
from src.tools.users import check_staff_permission
from src.services.base import publisher_crud

logger = logging.getLogger('publishers')

router = APIRouter()


@router.post(
    '/',
    response_model=pub_dev_schema.PubDevInDB,
    status_code=status.HTTP_201_CREATED,
    description='Create new publisher.'
)
async def create_publisher(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        publisher_in: pub_dev_schema.PubDevCreate
) -> Any:
    """
    Create new publisher.
    """
    check_staff_permission(current_user)
    publisher_obj = await publisher_crud.get_by_name(db=db, obj_in=publisher_in)
    if publisher_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Publisher with this name exists.'
        )
    publisher = await publisher_crud.create(db=db, obj_in=publisher_in)
    logger.info('Create publisher - %s, by user - %s,', publisher.name, current_user.username)
    return publisher


@router.get(
    '/',
    response_model=pub_dev_schema.PubDevMulti,
    status_code=status.HTTP_200_OK,
    description='Get list og publishers.'
)
async def get_publishers(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 50
) -> Any:
    """
    Retrieve publishers.
    """
    publishers = await publisher_crud.get_multi(db=db, skip=skip, limit=limit)
    logger.info('Return list of publishers to user with id %s', current_user.id)
    return publishers


@router.get(
    '/{publisher_id}',
    response_model=pub_dev_schema.PubDevInDB,
    status_code=status.HTTP_200_OK,
    description='Get publisher info by id.'
)
async def get_publisher(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        publisher_id: str
) -> Any:
    """
    Get publisher by id.
    """
    publisher_obj = await check_publisher_by_id(db=db, publisher_id=publisher_id)
    logger.info('Return publisher info with id %s to user with id %s', publisher_obj.id, current_user.id)
    return publisher_obj


@router.patch(
    '/{publisher_id}',
    response_model=pub_dev_schema.PubDevInDB,
    status_code=status.HTTP_200_OK,
    description='Partial update publisher info.'
)
async def patch_publisher(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        publisher_id: str,
        publisher_in: pub_dev_schema.PubDevUpdate
) -> Any:
    """
    Patch publisher info.
    """
    check_staff_permission(cur_user_obj=current_user)
    publisher_obj = await check_publisher_by_id(db=db, publisher_id=publisher_id)
    publisher_name_before = publisher_obj.name
    await check_duplicating_publisher(publisher_in=publisher_in, db=db, publisher_obj=publisher_obj)
    publisher_obj_patched = await publisher_crud.patch(
        db=db,
        obj_in=publisher_in,
        obj=publisher_obj
    )
    logger.info(
        'Partial update publisher %s (new name is %s) info.',
        publisher_name_before,
        publisher_obj_patched.name if publisher_name_before != publisher_obj_patched.name else publisher_name_before
    )
    return publisher_obj_patched


@router.delete(
    '/{publisher_id}',
    description='Delete publisher.',
    responses={
        status.HTTP_200_OK: {
            'model': pub_dev_schema.PubDevDelete,
            'description': 'Delete publisher.'
        }
    }
)
async def delete_publisher(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        publisher_id: str
) -> Any:
    """
    Delete publisher.
    """
    check_staff_permission(cur_user_obj=current_user)
    publisher_obj = await check_publisher_by_id(db=db, publisher_id=publisher_id)
    await publisher_crud.delete(db=db, obj=publisher_obj)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'info': f'Publisher {publisher_id} has been deleted.'
        }
    )
