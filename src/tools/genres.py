from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.services.base import genre_crud
from src.models.models import Genre
from src.schemas import genres as genre_schema


async def check_genre_by_id(db: AsyncSession, genre_id: str) -> Genre:
    genre_obj = await genre_crud.get_by_id(db=db, genre_id=genre_id)
    if not genre_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Genre not found.'
        )
    return genre_obj


async def check_duplicating_genre(
        genre_in: genre_schema.GenreUpdate,
        db: AsyncSession,
        genre_obj: Genre
) -> None:
    genre_in_data = jsonable_encoder(genre_in, exclude_none=True)
    if 'name' in genre_in_data:
        genre = await genre_crud.get_by_name(db=db, obj_in=genre_in)
        if genre and genre_obj.id != genre.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Genre with this name already exists'
            )
