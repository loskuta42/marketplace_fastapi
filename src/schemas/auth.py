from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str


class TokenUI(Token):
    pass


class TokenData(BaseModel):
    username: Optional[str] = None


class ResetToken(BaseModel):
    access_token: str
