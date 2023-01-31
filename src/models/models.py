import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy_utils import UUIDType, EmailType, ChoiceType

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

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_staff(self):
        return self.is_admin or self.is_moderator
