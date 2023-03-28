from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from src.models.models import Game
from src.services.base import game_crud
from src.schemas import games as games_schema


async def check_game_by_id(db: AsyncSession, game_id: str) -> Game:
    game_obj = await game_crud.get_by_id(db=db, game_id=game_id)
    if not game_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='game not found.'
        )
    return game_obj


async def check_duplicating_game(
        game_in: games_schema.GameUpdate,
        db: AsyncSession,
        game_obj: Game
) -> None:
    game_in_data = jsonable_encoder(game_in, exclude_none=True)
    if 'name' in game_in_data:
        game = await game_crud.get_by_name(db=db, obj_in=game_in)
        if game and game_obj.id != game.id and sorted(game_obj.platforms, key=lambda x: x.name) != game.platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Game with this name already exists'
            )
