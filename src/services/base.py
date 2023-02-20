from src.models.models import (
    User as UserModel,
    Genre as GenreModel
)
from src.schemas.users import UserRegister, UserUpgrade, ForgetPasswordRequestBody
from src.schemas.genres import GenreCreate, GenreUpdate

from .users import RepositoryUserDB
from .genres import RepositoryGenreDB


class RepositoryUser(
    RepositoryUserDB[
        UserModel,
        UserRegister,
        UserUpgrade,
        ForgetPasswordRequestBody
    ]
):
    pass


class RepositoryGenre(
    RepositoryGenreDB[
        GenreModel,
        GenreCreate,
        GenreUpdate
    ]
):
    pass


user_crud = RepositoryUser(UserModel)
genre_crud = RepositoryGenre(GenreModel)
