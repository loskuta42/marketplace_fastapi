from datetime import datetime
from typing import Optional

from pydantic import EmailStr, UUID1, BaseModel, validator
from fastapi import HTTPException, status

from .auth import Token
from src.models.enums import UserRoles


class ORM(BaseModel):
    class Config:
        orm_mode = True


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


class ForgetPasswordResponse(UserDelete):
    pass


class ForgetPasswordRequestBody(BaseModel):
    email: EmailStr


class ResetToken(Token):
    pass


class ResetPasswordResponse(UserDelete):
    pass


class ChangePasswordResponse(ResetPasswordResponse):
    pass


class ResetPassword(BaseModel):
    new_password: str
    re_new_password: str

    @validator('re_new_password', pre=True)
    def validate_re_password(cls, value, values):
        if value != values['new_password']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='re_new_password must be equel to new_password'
            )
        return value


class ChangePassword(ResetPassword):
    old_password: str
