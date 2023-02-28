import logging.config
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User
from src.schemas import genres as genre_schema
from src.db.db import get_session
from src.services.authorization import get_current_user
from src.services.base import genre_crud
from src.tools.base import check_required_fields
from src.tools.users import check_staff_permission
from src.tools.genres import check_genre_by_id, check_duplicating_genre


logger = logging.getLogger('users')

router = APIRouter()


@router.post(
    '/',
    response_model=genre_schema.GenreInDB,
    status_code=status.HTTP_201_CREATED,
    description='Create new genre.'
)
async def create_genre(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        genre_in: genre_schema.GenreCreate
) -> Any:
    """
    Create new genre.
    """
    check_staff_permission(current_user)
    genre_obj = await genre_crud.get_by_name(db=db, obj_in=genre_in)
    if genre_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Genre with this name exists.'
        )
    print('---before')
    genre = await genre_crud.create(db=db, obj_in=genre_in)
    print('---after', genre.games)
    logger.info('Create genre - %s, by user - %s', genre.name, current_user.username)
    return genre


@router.get(
    '/',
    response_model=genre_schema.GenreMulti,
    status_code=status.HTTP_200_OK,
    description='Get list of genres.'
)
async def get_genres(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 50
) -> Any:
    """
    Retrieve genres.
    """
    genres = await genre_crud.get_multi(db=db, skip=skip, limit=limit)
    logger.info('Return list of genres to user with id %s', current_user.id)
    return genres


@router.get(
    '/{genre_id}',
    response_model=genre_schema.GenreInDB,
    status_code=status.HTTP_200_OK,
    description='Get genre info by id.'
)
async def get_genre(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        genre_id: str
) -> Any:
    """
    Get genre by id.
    """
    genre_obj = await check_genre_by_id(db=db, genre_id=genre_id)
    logger.info('Return genre info with id %s to user with id %s', genre_id, current_user.id)
    return genre_obj


@router.patch(
    '/{genre_id}',
    response_model=genre_schema.GenreInDB,
    status_code=status.HTTP_200_OK,
    description='Partial update genre info.'
)
async def patch_genre(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        genre_id: str,
        genre_in: genre_schema.GenreUpdate
) -> Any:
    """
    Patch genre info.
    """
    check_staff_permission(cur_user_obj=current_user)
    genre_obj = await check_genre_by_id(db=db, genre_id=genre_id)
    await check_duplicating_genre(genre_in=genre_in, db=db, genre_obj=genre_obj)
    genre_obj_patched = await genre_crud.patch(
        db=db,
        obj_in=genre_in,
        genre_obj=genre_obj
    )
    logger.info(
        'Partial update %s (new name is %s) info.',
        genre_obj.name,
        genre_obj_patched.name if genre_obj.name != genre_obj_patched.name else genre_obj.name)
    return genre_obj_patched


@router.delete(
    '/{genre_id}',
    description='Delete genre.',
    responses={
        status.HTTP_200_OK: {
            'model': genre_schema.GenreDelete,
            'description': 'Delete genre.'
        }
    }
)
async def delete_genre(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        genre_id: str
) -> Any:
    """
    Delete genre.
    """
    check_staff_permission(cur_user_obj=current_user)
    genre_obj = await check_genre_by_id(db=db, genre_id=genre_id)
    await genre_crud.delete(db=db, genre_obj=genre_obj)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'info': f'Genre {genre_id} has been deleted.'
        }
    )
