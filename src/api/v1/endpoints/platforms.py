import logging.config
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.models.models import User
from src.schemas import platforms as platforms_schema
from src.services.authorization import get_current_user
from src.tools.platforms import check_platform_by_id, check_duplicating_platform
from src.tools.users import check_staff_permission
from src.services.base import platform_crud

logger = logging.getLogger('platforms')

router = APIRouter()


@router.post(
    '/',
    response_model=platforms_schema.PlatformInDB,
    status_code=status.HTTP_201_CREATED,
    description='Create new platform.'
)
async def create_platform(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        platform_in: platforms_schema.PlatformCreate
) -> Any:
    """
    Create new platform.
    """
    check_staff_permission(current_user)
    platform_obj = await platform_crud.get_by_name(db=db, obj_in=platform_in)
    if platform_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='platform with this name exists.'
        )
    platform = await platform_crud.create(db=db, obj_in=platform_in)
    logger.info('Create platform - %s, by user - %s,', platform.name, current_user.username)
    return platform


@router.get(
    '/',
    response_model=platforms_schema.PlatformMulti,
    status_code=status.HTTP_200_OK,
    description='Get list of platforms.'
)
async def get_platforms(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 50
) -> Any:
    """
    Retrieve platforms.
    """
    platforms = await platform_crud.get_multi(db=db, skip=skip, limit=limit)
    logger.info('Return list of platforms to user with id %s', current_user.id)
    return platforms


@router.get(
    '/{platform_id}',
    response_model=platforms_schema.PlatformInDB,
    status_code=status.HTTP_200_OK,
    description='Get platform info by id.'
)
async def get_platform(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        platform_id: str
) -> Any:
    """
    Get platform by id.
    """
    platform_obj = await check_platform_by_id(db=db, platform_id=platform_id)
    logger.info('Return platform info with id %s to user with id %s', platform_obj.id, current_user.id)
    return platform_obj


@router.patch(
    '/{platform_id}',
    response_model=platforms_schema.PlatformInDB,
    status_code=status.HTTP_200_OK,
    description='Partial update platform info.'
)
async def patch_platform(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        platform_id: str,
        platform_in: platforms_schema.PlatformUpdate
) -> Any:
    """
    Patch platform info.
    """
    check_staff_permission(cur_user_obj=current_user)
    platform_obj = await check_platform_by_id(db=db, platform_id=platform_id)
    platform_name_before = platform_obj.name
    await check_duplicating_platform(platform_in=platform_in, db=db, platform_obj=platform_obj)
    platform_obj_patched = await platform_crud.patch(
        db=db,
        obj_in=platform_in,
        obj=platform_obj
    )
    logger.info(
        'Partial update platform %s (new name is %s) info.',
        platform_name_before,
        platform_obj_patched.name if platform_name_before != platform_obj_patched.name else platform_name_before
    )
    return platform_obj_patched


@router.delete(
    '/{platform_id}',
    description='Delete platform.',
    responses={
        status.HTTP_200_OK: {
            'model': platforms_schema.PlatformDelete,
            'description': 'Delete platform.'
        }
    }
)
async def delete_platform(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        platform_id: str
) -> Any:
    """
    Delete platform.
    """
    check_staff_permission(cur_user_obj=current_user)
    platform_obj = await check_platform_by_id(db=db, platform_id=platform_id)
    await platform_crud.delete(db=db, obj=platform_obj)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'info': f'Platform {platform_id} has been deleted.'
        }
    )
