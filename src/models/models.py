import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy_utils import UUIDType, EmailType

from src.db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    username = Column(String(125), nullable=False, unique=True)
    email = Column(EmailType(255), nullable=False, unique=True)
    hashed_password = Column(String(125), nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
