from pydantic.types import UUID1
from pydantic import BaseModel

from .users import ORM


class PubDevCreate(ORM):
    name: str
    country: str


class PubDevUpdate(PubDevCreate):
    name: str | None = None
    country: str | None = None


class PubDevInDB(PubDevCreate):
    id: UUID1
    games: list = []


class PubDev(PubDevCreate):
    id: UUID1


class PubDevMulti(BaseModel):
    __root__: list[PubDevInDB]


class PubDevDelete(BaseModel):
    info: str
