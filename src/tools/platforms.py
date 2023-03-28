from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.models.models import Platform
from src.services.base import platform_crud
from src.schemas import platforms as platforms_schema


async def check_platform_by_id(db: AsyncSession, platform_id: str) -> Platform:
    platform_obj = await platform_crud.get_by_id(db=db, platform_id=platform_id)
    if not platform_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Platform not found.'
        )
    return platform_obj


async def check_duplicating_platform(
        platform_in: platforms_schema.PlatformUpdate,
        db: AsyncSession,
        platform_obj: Platform
) -> None:
    platform_in_data = jsonable_encoder(platform_in, exclude_none=True)
    if 'name' in platform_in_data:
        platform = await platform_crud.get_by_name(db=db, obj_in=platform_in)
        if platform and platform_obj.id != platform.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Platform with this name already exists'
            )
