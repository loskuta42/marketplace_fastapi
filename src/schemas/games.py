from datetime import datetime
from decimal import Decimal

from pydantic.types import UUID1
from pydantic import BaseModel, condecimal

from .users import ORM
from .genres import GenreInDB
from .platforms import PlatformInDB
from .pub_dev import PubDevInDB


class GameCreate(ORM):
    name: str
    price: condecimal(gt=Decimal('0.00'))
    discount: condecimal(ge=Decimal('0.00')) = Decimal('0.00')
    description: str
    release_date: datetime
    genres: list[GenreInDB]
    developers: list[PubDevInDB]
    publishers: list[PubDevInDB]
    platforms: list[PlatformInDB]
    

class GameUpdate(GameCreate):
    pass


class GameInDB(GameCreate):
    id: UUID1


class GameMulti(BaseModel):
    __root__: list[GameInDB]
