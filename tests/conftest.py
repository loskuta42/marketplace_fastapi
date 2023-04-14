import asyncio
import json

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
from fastapi import FastAPI

from src.db.db import Base, get_session
from src.core.config import app_settings
from src.main import app
from src.services.base import user_crud, genre_crud, publisher_crud, developer_crud, platform_crud, game_crud
from src.models.models import User, Genre, Publisher, Developer, Platform, Game
from src.models.enums import UserRoles
from src.schemas import games as games_schema

DATABASE_URL = 'sqlite+aiosqlite:///./test.db'


@pytest.fixture(scope='session')
def base_url():
    return f'http://{app_settings.project_host}:{app_settings.project_port}'


def get_test_engine():
    return create_async_engine(DATABASE_URL, echo=True, future=True)


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def engine():
    engine = get_test_engine()
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture(scope='session')
def async_session(engine):
    return async_sessionmaker(
        engine, expire_on_commit=False
    )


@pytest_asyncio.fixture(scope='session')
async def gen_async_session(async_session) -> AsyncSession:
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope='session')
async def create_base(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='session')
async def test_app(engine, create_base):
    async_session = async_sessionmaker(
        engine, expire_on_commit=False
    )

    async def get_test_session() -> AsyncSession:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    yield app


@pytest_asyncio.fixture(scope='session')
async def async_client(test_app: FastAPI, base_url: str):
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        yield ac


@pytest_asyncio.fixture(scope='session')
async def auth_async_client(gen_async_session: AsyncSession, test_app: FastAPI, base_url: str):
    input_data = {
        'username': 'test_user_auth',
        'password': 'test_password_auth',
        'email': 'test_user_auth@example.com'
    }
    db = gen_async_session
    await user_crud.create(db=db, obj_in=input_data)
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        response_success = await ac.post(
            test_app.url_path_for('get_token_for_user'),
            json=input_data
        )
        token = 'Bearer ' + response_success.json()['access_token']
        ac.headers = {'Authorization': token}
        yield ac


@pytest_asyncio.fixture(scope='session')
async def auth_async_admin_client(gen_async_session: AsyncSession, test_app: FastAPI, base_url: str):
    input_data = {
        'username': 'test_user_admin',
        'password': 'test_admin_password',
        'email': 'test_admin@example.com',
        'role': UserRoles.ADMIN
    }
    db = gen_async_session
    await user_crud.create(db=db, obj_in=input_data)
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        response_success = await ac.post(
            test_app.url_path_for('get_token_for_user'),
            json=input_data
        )
        token = 'Bearer ' + response_success.json()['access_token']
        ac.headers = {'Authorization': token}
        yield ac


@pytest_asyncio.fixture(scope='session')
async def new_user(gen_async_session: AsyncSession) -> User:
    gen_numbers = (number for number in range(1, 100))
    num = next(gen_numbers)
    data = {
        'username': f'test_user{num}',
        'password': f'test_password{num}',
        'email': f'test_user{num}@example.com'
    }
    db = gen_async_session
    user = await user_crud.create(db=db, obj_in=data)
    yield user


@pytest_asyncio.fixture(scope='session')
async def new_admin(gen_async_session: AsyncSession) -> User:
    data = {
        'username': 'admin_user',
        'password': 'admin_password',
        'email': 'admin@example.com',
        'role': UserRoles.ADMIN
    }
    db = gen_async_session
    user_admin = await user_crud.create(db=db, obj_in=data)
    return user_admin


@pytest_asyncio.fixture(scope='session')
async def new_genre(gen_async_session: AsyncSession) -> Genre:
    data = {
        'name': 'test_genre',
        'description': 'test_genre_description'
    }
    db = gen_async_session
    genre_obj = await genre_crud.create(db=db, obj_in=data)
    return genre_obj


@pytest_asyncio.fixture(scope='session')
async def new_publisher(gen_async_session: AsyncSession) -> Publisher:
    data = {
        'name': 'test_publisher',
        'country': 'test_publisher_country'
    }
    db = gen_async_session
    publisher_obj = await publisher_crud.create(db=db, obj_in=data)
    return publisher_obj


@pytest_asyncio.fixture(scope='session')
async def new_developer(gen_async_session: AsyncSession) -> Developer:
    data = {
        'name': 'test_developer',
        'country': 'test_developer_country'
    }
    db = gen_async_session
    developer_obj = await developer_crud.create(db=db, obj_in=data)
    return developer_obj


@pytest_asyncio.fixture(scope='session')
async def new_platform(gen_async_session: AsyncSession) -> Platform:
    data = {
        'name': 'test_platform',
    }
    db = gen_async_session
    platform_obj = await platform_crud.create(db=db, obj_in=data)
    return platform_obj


@pytest_asyncio.fixture(scope='session')
async def new_game(gen_async_session: AsyncSession) -> Game:
    db = gen_async_session
    genre_obj = await genre_crud.create(
        db=db,
        obj_in={
            'name': 'test_game_genre',
            'description': 'test_game_genre_description'
        }
    )
    publisher_obj = await publisher_crud.create(
        db=db,
        obj_in={
            'name': 'test_game_publisher',
            'country': 'test_game_publisher_country'
        }
    )
    developer_obj = await developer_crud.create(
        db=db,
        obj_in={
            'name': 'test_game_developer',
            'country': 'test_game_developer_country'
        }
    )
    platform_obj = await platform_crud.create(
        db=db,
        obj_in={
            'name': 'test_game_platform',
        }
    )
    d_data = {
            'name': 'test_game',
            'price': 0.11,
            'discount': 0.12,
            'description': 'test_game_description',
            'genres': [genre_obj.name],
            'release_date': '06.05.2005',
            'developers': [developer_obj.name],
            'publishers': [publisher_obj.name],
            'platforms': [platform_obj.name]
        }
    data = games_schema.GameCreate(**d_data)

    game_obj = await game_crud.create(
        db=db,
        obj_in=data
    )
    return game_obj
