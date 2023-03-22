from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.models.models import Developer
from src.services.base import developer_crud
from src.schemas import pub_dev as pub_dev_schema


async def check_developer_by_id(db: AsyncSession, developer_id: str) -> Developer:
    developer_obj = await developer_crud.get_by_id(db=db, entity_id=developer_id)
    if not developer_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Developer not found.'
        )
    return developer_obj


async def check_duplicating_developer(
        developer_in: pub_dev_schema.PubDevUpdate,
        db: AsyncSession,
        developer_obj: Developer
) -> None:
    developer_in_data = jsonable_encoder(developer_in, exclude_none=True)
    if 'name' in developer_in_data:
        developer = await developer_crud.get_by_name(db=db, obj_in=developer_in)
        if developer and developer_obj.id != developer.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Developer with this name already exists'
            )
