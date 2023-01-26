from src.models.models import User as UserModel
from src.schemas.user import UserRegister, UserUpgrade

from .user import RepositoryUserDB


class RepositoryUser(
    RepositoryUserDB[
        UserModel,
        UserRegister,
        UserUpgrade
    ]
):
    pass


user_crud = RepositoryUser(UserModel)
