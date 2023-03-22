from datetime import datetime

from pydantic.types import UUID1
from pydantic import BaseModel

from .users import ORM


class PlatformCreate(ORM):
    name: str


class PlatformUpdate(PlatformCreate):
    pass


class PlatformInDB(PlatformCreate):
    id: UUID1
    games: list = []


class PlatformMulti(BaseModel):
    __root__: list[PlatformInDB]


class PlatformDelete(BaseModel):
    info: str
