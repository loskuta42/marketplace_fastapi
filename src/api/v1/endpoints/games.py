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
        game_in: games_schema.gameCreate
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
