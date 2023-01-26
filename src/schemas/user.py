from datetime import datetime
from pydantic import EmailStr, UUID1

from .auth import ORM


class User(ORM):
    username: str
    email: EmailStr


class UserRegister(User):
    password: str


class UserUpgrade(User):
    pass


class UserAuth(UserRegister):
    pass


class UserRegisterResponse(User):
    created_at: datetime


class UserInDB(User):
    id: UUID1
    created_at: datetime