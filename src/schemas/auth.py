from typing import Optional

from pydantic import BaseModel


class ORM(BaseModel):
    class Config:
        orm_mode = True


class Token(ORM):
    access_token: str


class TokenUI(Token):
    pass


class TokenData(ORM):
    username: Optional[str] = None
