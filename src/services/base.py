from src.models.models import User as UserModel
from src.schemas.users import UserRegister, UserUpgrade, ForgetPasswordRequestBody

from .users import RepositoryUserDB


class RepositoryUser(
    RepositoryUserDB[
        UserModel,
        UserRegister,
        UserUpgrade,
        ForgetPasswordRequestBody
    ]
):
    pass


user_crud = RepositoryUser(UserModel)
