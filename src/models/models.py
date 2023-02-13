import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text, event, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import UUIDType, EmailType, ChoiceType
from slugify import slugify

from src.db.db import Base
from .enums import UserRoles


class User(Base):
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


class Category(Base):
    __tablename__ = 'categories'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(75), nullable=False, unique=True)
    slug = Column(String(75))
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    description = Column(Text(255), nullable=True)
    parent_id = Column(UUIDType(binary=False), ForeignKey('categories.id'))
    children = relationship('Category', backref=backref('parent', remote_side=[id]))

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


class Item(Base):
    __tablename__ = 'items'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    name = Column(String(75), nullable=False)



event.listen(Category.name, 'set', Category.generate_slug, retval=False)

