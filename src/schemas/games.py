from datetime import date, datetime
from decimal import Decimal

from pydantic.types import UUID1
from pydantic import BaseModel, condecimal, validator

from .users import ORM
from .genres import Genre
from .pub_dev import PubDev
from .platforms import Platform


class GameCreate(ORM):
    name: str
    price: condecimal(gt=Decimal('0.00'))
    discount: condecimal(ge=Decimal('0.00')) = Decimal('0.00')
    description: str
    release_date: date
    genres: list[str]
    developers: list[str]
    publishers: list[str]
    platforms: list[str]

    @validator('release_date', pre=True, always=True)
    def convert_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%d.%m.%Y').date()
        return v


class GameUpdate(GameCreate):
    name: str | None = None
    price: condecimal(gt=Decimal('0.00')) | None = None
    discount: condecimal(ge=Decimal('0.00')) | None = Decimal('0.00')
    description: str | None = None
    release_date: date | None = None
    genres: list[str] | None = None
    developers: list[str] | None = None
    publishers: list[str] | None = None
    platforms: list[str] | None = None

    @validator('release_date', pre=True, always=True)
    def convert_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%d.%m.%Y').date()
        return v


class GameInDB(GameCreate):
    id: UUID1
    genres: list[Genre]
    developers: list[PubDev]
    publishers: list[PubDev]
    platforms: list[Platform]


class Game(GameCreate):
    id: UUID1


class GameMulti(BaseModel):
    __root__: list[GameInDB]


class GameDelete(BaseModel):
    info: str
