import logging.config
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.models.models import User
from src.schemas import games as games_schema
from src.services.authorization import get_current_user
from src.tools.games import check_game_by_id, check_duplicating_game
from src.tools.users import check_staff_permission
from src.services.base import game_crud

logger = logging.getLogger('games')

router = APIRouter()


@router.post(
    '/',
    response_model=games_schema.GameInDB,
    status_code=status.HTTP_201_CREATED,
    description='Create new game.'
)
async def create_game(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        game_in: games_schema.GameCreate
) -> Any:
    """
    Create new game.
    """
    check_staff_permission(current_user)
    game_obj = await game_crud.get_by_name(db=db, obj_in=game_in)
    if game_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Game with this name exists.'
        )
    game = await game_crud.create(db=db, obj_in=game_in)
    logger.info('Create game - %s, by user - %s,', game.name, current_user.username)
    return game


@router.get(
    '/',
    response_model=games_schema.GameMulti,
    status_code=status.HTTP_200_OK,
    description='Get list of games.'
)
async def get_games(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 50
) -> Any:
    """
    Retrieve games.
    """
    games = await game_crud.get_multi(db=db, skip=skip, limit=limit)
    logger.info('Return list of games to user with id %s', current_user.id)
    return games


@router.get(
    '/{game_id}',
    response_model=games_schema.GameInDB,
    status_code=status.HTTP_200_OK,
    description='Get game info by id.'
)
async def get_game(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        game_id: str
) -> Any:
    """
    Get game by id.
    """
    game_obj = await check_game_by_id(db=db, game_id=game_id)
    logger.info('Return game info with id %s to user with id %s', game_obj.id, current_user.id)
    return game_obj


@router.patch(
    '/{game_id}',
    response_model=games_schema.GameInDB,
    status_code=status.HTTP_200_OK,
    description='Partial update game info.'
)
async def patch_game(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        game_id: str,
        game_in: games_schema.GameUpdate
) -> Any:
    """
    Patch game info.
    """
    check_staff_permission(cur_user_obj=current_user)
    game_obj = await check_game_by_id(db=db, game_id=game_id)
    game_name_before = game_obj.name
    await check_duplicating_game(db=db, game_in=game_in, game_obj=game_obj)
    game_obj_patched = await game_crud.patch(
        db=db,
        obj_in=game_in,
        obj=game_obj
    )
    logger.info(
        'Partial update platform %s (new name is %s) info.',
        game_name_before,
        game_obj_patched.name if game_name_before != game_obj_patched.name else game_name_before
    )
    return game_obj_patched


@router.delete(
    '/{game_id}',
    description='Delete game',
    responses={
        status.HTTP_200_OK: {
            'model': games_schema.GameDelete,
            'description': 'Delete game.'
        }
    }
)
async def delete_game(
        *,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
        game_id: str
) -> Any:
    """
    Delete game.
    """
    check_staff_permission(cur_user_obj=current_user)
    game_obj = await  check_game_by_id(db=db, game_id=game_id)
    await game_crud.delete(db=db, obj=game_obj)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'info': f'Platform {game_id} has been deleted.'
        }
    )
