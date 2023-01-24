from src.models.models import User as UserModel
from src.schemas.user import UserRegister

from .user import RepositoryUserDB


class RepositoryUser(
    RepositoryUserDB[
        UserModel,
        UserRegister
    ]
):
    pass


user_crud = RepositoryUser(UserModel)
