import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text, event, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import UUIDType, EmailType, ChoiceType
from slugify import slugify

from src.db.db import Base
from .enums import UserRoles


class User(Base):
    """Users db model."""

    __tablename__ = 'users'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    username = Column(String(125), nullable=False, unique=True)
    email = Column(EmailType(255), nullable=False, unique=True)
    hashed_password = Column(String(125), nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    role = Column(ChoiceType(choices=UserRoles, impl=Integer()), default=UserRoles.USER)
    reset_token = Column(String(500), nullable=True, default=None)

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_staff(self):
        return self.is_admin or self.is_moderator


class Genre(Base):
    """Genre db model."""
    __tablename__ = 'genres'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(75), nullable=False, unique=True)
    slug = Column(String(75))
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    description = Column(Text(255), nullable=True)
    # parent_id = Column(UUIDType(binary=False), ForeignKey('categories.id'))
    # children = relationship('Genre', backref=backref('parent', remote_side=[id]))
    games = relationship('Game', secondary='genres_games', back_populates='genres')

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


class Publisher(Base):
    """Publisher db model."""
    __tablename__ = 'publishers'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(150), nullable=False)
    country = Column(String(150))
    games = relationship('Game', secondary='publishers_games', back_populates='publishers')


class Developer(Base):
    """Developer db model."""
    __tablename__ = 'developers'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(150), nullable=False)
    country = Column(String(150))
    games = relationship('Game', secondary='developers_games', back_populates='developers')


class Game(Base):
    __tablename__ = 'games'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(75), nullable=False)
    price = Column(Float(precision=2, asdecimal=True))
    discount = Column(Float(precision=2, asdecimal=True))
    description = Column(Text(500))
    genres = relationship('Genre', secondary='genres_games', back_populates='games')
    release_date = Column(DateTime, index=True, nullable=False)
    developers = relationship('Developer', secondary='developers_games', back_populates='games')
    publishers = relationship('Publisher', secondary='publishers_games', back_populates='games')
    platform = Column(UUIDType(binary=False), ForeignKey('platforms.id'))


class GenreGame(Base):
    """Genres to games many-to-many model."""

    __tablename__ = 'genres_games'

    genre_id = Column(UUIDType(binary=False), ForeignKey('genres.id'), primary_key=True)
    game_id = Column(UUIDType(binary=False), ForeignKey('games.id'), primary_key=True)


class DeveloperGame(Base):
    """Developers to games many-to-many model."""

    __tablename__ = 'developers_games'

    developer_id = Column(UUIDType(binary=False), ForeignKey('developers.id'), primary_key=True)
    game_id = Column(UUIDType(binary=False), ForeignKey('games.id'), primary_key=True)


class PublisherGame(Base):
    """Publishers to games many-to-many model."""

    __tablename__ = 'publishers_games'

    publisher_id = Column(UUIDType(binary=False), ForeignKey('publishers.id'), primary_key=True)
    game_id = Column(UUIDType(binary=False), ForeignKey('games.id'), primary_key=True)


class Platform(Base):
    """Platform db model."""

    __tablename__ = 'platforms'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(75), nullable=False)
    games = relationship('Game', backref='platform', lazy='dynamic')


event.listen(Genre.name, 'set', Genre.generate_slug, retval=False)
