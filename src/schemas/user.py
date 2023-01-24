from datetime import datetime
from pydantic import EmailStr

from auth import ORM


class User(ORM):
    username: str
    email: EmailStr


class UserRegister(User):
    password: str


class UserAuth(UserRegister):
    pass


class UserRegisterResponse(User):
    created_at: datetime
