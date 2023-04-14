from typing import TypeVar, Generic, Type, Optional, Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder

from src.db.db import Base
from .repository_base import Repository
from src.models.models import Genre, Publisher, Platform, Developer

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class RepositoryGameDB(
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
            game_id: str
    ) -> Optional[ModelType]:
        statement = select(
            self._model
        ).where(
            self._model.id == game_id
        ).options(
            selectinload(self._model.genres),
            selectinload(self._model.publishers),
            selectinload(self._model.developers),
            selectinload(self._model.platforms)
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_name(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType | UpdateSchemaType
    ) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(
            self._model
        ).where(
            self._model.name == obj_in_data['name']
        ).options(
            selectinload(self._model.genres),
            selectinload(self._model.publishers),
            selectinload(self._model.developers),
            selectinload(self._model.platforms)
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
        statement = select(
            self._model
        ).offset(skip).limit(limit).options(
            selectinload(self._model.genres),
            selectinload(self._model.publishers),
            selectinload(self._model.developers),
            selectinload(self._model.platforms)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def _object_in_edit(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType
    ):
        obj_in_data = jsonable_encoder(obj_in, exclude_none=True)
        obj_in_data['release_date'] = obj_in.release_date
        name_to_model = {
            'genres': Genre,
            'developers': Developer,
            'publishers': Publisher,
            'platforms': Platform
        }
        for key in obj_in_data.keys():
            if key in name_to_model:
                model = name_to_model[key]
                names = obj_in_data[key]
                print(model, names)
                statement = select(
                    model
                ).filter(
                    model.name.in_(tuple(names))
                ).options(
                    selectinload(model.games)
                )
                results = await db.execute(statement=statement)
                obj_in_data[key] = results.scalars().all()
        return obj_in_data

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = await self._object_in_edit(db=db, obj_in=obj_in)

        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def patch(
            self,
            db: AsyncSession,
            *,
            obj: ModelType,
            obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        obj_in_data = await self._object_in_edit(db=db, obj_in=obj_in)
        for key, value in obj_in_data.items():
            setattr(obj, key, value)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(
            self,
            db: AsyncSession,
            *,
            obj: ModelType
    ) -> None:
        await db.delete(obj)
        await db.commit()
