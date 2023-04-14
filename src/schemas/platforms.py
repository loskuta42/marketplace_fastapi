from datetime import datetime

from pydantic.types import UUID1
from pydantic import BaseModel

from .users import ORM


class PlatformCreate(ORM):
    name: str


class PlatformUpdate(PlatformCreate):
    name: str | None = None


class PlatformInDB(PlatformCreate):
    id: UUID1
    games: list = []


class Platform(PlatformCreate):
    id: UUID1


class PlatformMulti(BaseModel):
    __root__: list[PlatformInDB]


class PlatformDelete(BaseModel):
    info: str
