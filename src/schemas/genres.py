from datetime import datetime

from pydantic.types import UUID1
from pydantic import BaseModel

from .users import ORM


class GenreCreate(ORM):
    name: str
    description: str


class GenreUpdate(ORM):
    name: str | None = None
    description: str | None = None


class GenreInDB(GenreCreate):
    id: UUID1
    created_at: datetime
    slug: str
    games: list = []


class Genre(GenreCreate):
    id: UUID1
    created_at: datetime
    slug: str


class GenreMulti(BaseModel):
    __root__: list[GenreInDB]


class GenreDelete(BaseModel):
    info: str
