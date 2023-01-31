import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from fastapi import FastAPI

from src.db.db import Base, get_session
from src.core.config import app_settings
from src.main import app
from src.services.base import user_crud
from src.models.models import User
from src.models.enums import UserRoles

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
    return sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
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
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
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
        'username': 'test_user',
        'password': 'test_password',
        'email': 'test_user@example.com'
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
    data = {
        'username': f'test_user{next(gen_numbers)}',
        'password': f'test_password{next(gen_numbers)}',
        'email': f'test_user{next(gen_numbers)}@example.com'
    }
    db = gen_async_session
    user = await user_crud.create(db=db, obj_in=data)
    return user


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
