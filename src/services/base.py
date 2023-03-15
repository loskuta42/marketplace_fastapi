from src.models.models import (
    User as UserModel,
    Genre as GenreModel,
    Publisher as PublisherModel,
    Developer as DeveloperModel
)
from src.schemas.users import UserRegister, UserUpgrade, ForgetPasswordRequestBody
from src.schemas.genres import GenreCreate, GenreUpdate
from src.schemas.pub_dev import PubDevCreate, PubDevUpdate

from .users import RepositoryUserDB
from .genres import RepositoryGenreDB
from .pub_dev import RepositoryDevPubDB


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


class RepositoryPubDev(
    RepositoryDevPubDB[
        PublisherModel | DeveloperModel,
        PubDevCreate,
        PubDevUpdate
    ]
):
    pass


user_crud = RepositoryUser(UserModel)
genre_crud = RepositoryGenre(GenreModel)
publisher_crud = RepositoryPubDev(PublisherModel)
developer_crud = RepositoryPubDev(DeveloperModel)
