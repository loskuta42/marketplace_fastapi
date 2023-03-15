from pydantic.types import UUID1
from pydantic import BaseModel

from .users import ORM


class PubDevCreate(ORM):
    name: str
    country: str


class PubDevUpdate(PubDevCreate):
    pass


class PubDevInDB(PubDevCreate):
    id: UUID1
    games: list = []


class PubDevMulti(BaseModel):
    __root__: list[PubDevInDB]


class PubDevDelete(BaseModel):
    info: str
