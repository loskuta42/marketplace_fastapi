from datetime import datetime
from typing import Optional

from pydantic import EmailStr, UUID1, BaseModel

from .auth import ORM
from src.models.enums import UserRoles


class User(ORM):
    username: str
    email: EmailStr


class UserRegister(User):
    password: str


class UserUpgrade(User):
    username: Optional[str]
    email: Optional[str]


class UserAuth(UserRegister):
    pass


class UserRegisterResponse(User):
    created_at: datetime


class UserInDB(User):
    id: UUID1
    created_at: datetime
    role: UserRoles


class UserMulti(BaseModel):
    __root__: list[UserInDB]


class UserDelete(BaseModel):
    info: str
