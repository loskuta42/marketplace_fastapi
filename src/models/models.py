import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, Text, event, ForeignKey, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column, WriteOnlyMapped
from sqlalchemy_utils import UUIDType, EmailType, ChoiceType
from slugify import slugify

from src.db.db import Base
from .enums import UserRoles


class User(Base):
    """Users db model."""

    __tablename__ = 'users'

    id: Mapped[uuid] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    username: Mapped[str] = mapped_column(String(125), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(EmailType(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(125), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    role: Mapped[UserRoles] = mapped_column(ChoiceType(choices=UserRoles, impl=Integer()), default=UserRoles.USER)
    reset_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, default=None)

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_staff(self):
        return self.is_admin or self.is_moderator

    def __repr__(self):
        return f'<User>: username:{ self.username }'


class Genre(Base):
    """Genre db model."""
    __tablename__ = 'genres'

    id: Mapped[uuid] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name: Mapped[str] = mapped_column(String(75), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(75))
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    description: Mapped[Optional[str]] = mapped_column(Text(255), nullable=True)
    # parent_id = Column(UUIDType(binary=False), ForeignKey('categories.id'))
    # children = relationship('Genre', backref=backref('parent', remote_side=[id]))
    games: Mapped[List['Game']] = relationship(secondary='genres_games', back_populates='genres', lazy='joined')

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


class Publisher(Base):
    """Publisher db model."""
    __tablename__ = 'publishers'

    id: Mapped[uuid] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(150))
    games: Mapped[List['Game']] = relationship(secondary='publishers_games', back_populates='publishers', lazy='joined')


class Developer(Base):
    """Developer db model."""
    __tablename__ = 'developers'

    id: Mapped[uuid] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    games: Mapped[List['Game']] = relationship(
        secondary='developers_games',
        back_populates='developers',
        lazy='joined'
    )


class Game(Base):
    """Game db model."""

    __tablename__ = 'games'

    id: Mapped[uuid] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name: Mapped[str] = mapped_column(String(75), nullable=False)
    price: Mapped[float] = mapped_column(Float(precision=2, asdecimal=True))
    discount: Mapped[float] = mapped_column(Float(precision=2, asdecimal=True), nullable=True, default=0.00)
    description: Mapped[str] = mapped_column(Text(500), nullable=False)
    genres: Mapped[List['Genre']] = relationship(secondary='genres_games', back_populates='games', lazy='joined')
    release_date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    developers: Mapped[List['Developer']] = relationship(
        secondary='developers_games',
        back_populates='games',
        lazy='joined'
    )
    publishers: Mapped[List['Publisher']] = relationship(
        secondary='publishers_games',
        back_populates='games',
        lazy='joined'
    )
    platform_id: Mapped[uuid] = mapped_column(UUIDType(binary=False), ForeignKey('platforms.id'))
    platform: Mapped['Platform'] = relationship(back_populates='games', lazy='joined')


class GenreGame(Base):
    """Genres to games many-to-many model."""

    __tablename__ = 'genres_games'

    genre_id: Mapped[uuid] = mapped_column(ForeignKey('genres.id'), primary_key=True)
    game_id: Mapped[uuid] = mapped_column(ForeignKey('games.id'), primary_key=True)


class DeveloperGame(Base):
    """Developers to games many-to-many model."""

    __tablename__ = 'developers_games'

    developer_id: Mapped[uuid] = mapped_column(UUIDType(binary=False), ForeignKey('developers.id'), primary_key=True)
    game_id: Mapped[uuid] = mapped_column(UUIDType(binary=False), ForeignKey('games.id'), primary_key=True)


class PublisherGame(Base):
    """Publishers to games many-to-many model."""

    __tablename__ = 'publishers_games'

    publisher_id: Mapped[uuid] = mapped_column(UUIDType(binary=False), ForeignKey('publishers.id'), primary_key=True)
    game_id: Mapped[uuid] = mapped_column(UUIDType(binary=False), ForeignKey('games.id'), primary_key=True)


class Platform(Base):
    """Platform db model."""

    __tablename__ = 'platforms'

    id: Mapped[uuid] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name: Mapped[str] = mapped_column(String(75), nullable=False)
    games: WriteOnlyMapped['Game'] = relationship(order_by='Game.release_date', lazy='joined')


event.listen(Genre.name, 'set', Genre.generate_slug, retval=False)
