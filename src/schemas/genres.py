from datetime import datetime

from pydantic.types import UUID1
from pydantic import BaseModel

from .users import ORM


class GenreCreate(ORM):
    name: str
    description: str
    games: list = []


class GenreUpdate(GenreCreate):
    pass


class GenreInDB(GenreCreate):
    id: UUID1
    created_at: datetime
    slug: str


class GenreMulti(BaseModel):
    __root__: list[GenreInDB]


class GenreDelete(BaseModel):
    info: str
