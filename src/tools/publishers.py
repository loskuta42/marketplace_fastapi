from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.models.models import Publisher
from src.services.base import publisher_crud
from src.schemas import pub_dev as pub_dev_schema


async def check_publisher_by_id(db: AsyncSession, publisher_id: str) -> Publisher:
    publisher_obj = await publisher_crud.get_by_id(db=db, entity_id=publisher_id)
    if not publisher_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Publisher not found.'
        )
    return publisher_obj


async def check_duplicating_publisher(
        publisher_in: pub_dev_schema.PubDevUpdate,
        db: AsyncSession,
        publisher_obj: Publisher
) -> None:
    publisher_in_data = jsonable_encoder(publisher_in, exclude_none=True)
    if 'name' in publisher_in_data:
        publisher = await publisher_crud.get_by_name(db=db, obj_in=publisher_in)
        if publisher and publisher_obj.id != publisher.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Publisher with this name already exists'
            )
