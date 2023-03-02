from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder

from src.db.db import Base


class Repository(ABC):

    @abstractmethod
    def get_by_id(self, *args, **kwargs):
        ...

    @abstractmethod
    def get_by_name(self, *args, **kwargs):
        ...

    @abstractmethod
    def get_by_slug(self, *args, **kwargs):
        ...

    @abstractmethod
    def get_multi(self, *args, **kwargs):
        ...

    @abstractmethod
    def create(self, *args, **kwargs):
        ...

    @abstractmethod
    def patch(self, *args, **kwargs):
        ...

    @abstractmethod
    def delete(self, *args, **kwargs):
        ...


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class RepositoryGenreDB(
    Repository,
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType
    ]
):
    def __init__(
            self,
            model: Type[ModelType]
    ):
        self._model = model

    async def get_by_id(
            self,
            db: AsyncSession,
            genre_id: str,
    ) -> Optional[ModelType]:
        statement = select(
            self._model
        ).where(
            self._model.id == genre_id
        ).options(
            selectinload(self._model.games)
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_name(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType | UpdateSchemaType,
    ) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(
            self._model
        ).where(
            self._model.name == obj_in_data['name']
        ).options(
            selectinload(self._model.games)
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_slug(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType | UpdateSchemaType,
    ) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(
            self._model
        ).where(
            self._model.slug == obj_in_data['slug']
        ).options(
            selectinload(self._model.games)
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
        statement = select(self._model).offset(skip).limit(limit).options(
            selectinload(self._model.games)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def patch(
            self,
            db: AsyncSession,
            *,
            genre_obj: ModelType,
            obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, exclude_none=True)

        for key, value in obj_in_data.items():
            setattr(genre_obj, key, value)
        db.add(genre_obj)
        await db.commit()
        await db.refresh(genre_obj)
        return genre_obj

    async def delete(
            self,
            db: AsyncSession,
            *,
            genre_obj: ModelType
    ) -> None:
        await db.delete(genre_obj)
        await db.commit()
