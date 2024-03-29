from typing import TypeVar, Generic, Type, Optional, Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.db import Base
from src.tools.password import get_password_hash
from .repository_base import Repository


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
ForgetPasswordSchemaType = TypeVar('ForgetPasswordSchemaType', bound=BaseModel)


class RepositoryUserDB(
    Repository,
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ForgetPasswordSchemaType
    ]
):
    def __init__(
            self,
            model: Type[ModelType]
    ):
        self._model = model

    async def get_by_username(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType | UpdateSchemaType,
    ) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(
            self._model
        ).where(
            self._model.username == obj_in_data['username']
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_email(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType | UpdateSchemaType | ForgetPasswordSchemaType
    ) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(
            self._model
        ).where(
            self._model.email == obj_in_data['email']
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_id(
            self,
            db: AsyncSession,
            user_id: Optional[str]
    ) -> Optional[ModelType]:
        statement = select(
            self._model
        ).where(
            self._model.id == user_id
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
            self,
            db: AsyncSession,
            *,
            skip=0,
            limit=100
    ) -> list[ModelType]:
        statement = select(self._model).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    def create_obj(self, obj_in_data: dict):
        password = obj_in_data.pop('password')
        obj_in_data['hashed_password'] = get_password_hash(password)
        return self._model(**obj_in_data)

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.create_obj(obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def patch(
            self,
            db: AsyncSession,
            *,
            user_obj: ModelType,
            obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, exclude_none=True)

        for key, value in obj_in_data.items():
            setattr(user_obj, key, value)
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)
        return user_obj

    async def delete(
            self,
            db: AsyncSession,
            *,
            user_obj: ModelType
    ) -> None:
        await db.delete(user_obj)
        await db.commit()
