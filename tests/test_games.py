from http import HTTPStatus

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.models.models import Game, Genre, Publisher, Developer, Platform
from src.schemas import games as game_schema


@pytest.mark.asyncio
async def test_01_games_create(
        test_app: FastAPI,
        auth_async_client: AsyncClient,
        auth_async_admin_client: AsyncClient,
        new_genre: Genre,
        new_publisher: Publisher,
        new_developer: Developer,
        new_platform: Platform
):
    data = {
        'name': 'test_game',
        'price': 0.11,
        'discount': 0.12,
        'description': 'test_game_description',
        'genres': [new_genre.name],
        'release_date': '06.05.2005',
        'publishers': [new_publisher.name],
        'developers': [new_developer.name],
        'platforms': [new_platform.name]
    }
    url = test_app.url_path_for('create_game')
    response = await auth_async_client.post(
        url,
        json=data
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that POST request to `/api/v1/games/` by not admin return 403 status code'
    )
    response = await auth_async_admin_client.post(
        url,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'Check that POST request to `/api/v1/games/` with no body and with admin rights return 422 status code'
    )
    response = await auth_async_admin_client.post(
        url,
        json=data
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Check that POST request to `/api/v1/games/` with admin rights return 201 status code'
    )
    response_data = response.json()
    field_names = game_schema.GameInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in response_data, (
            'Make sure that the POST request `/api/v1/games/` '
            f'returns {field_name} field'
        )

    input_fields = data.keys()
    for field_name in input_fields:
        res_data_value = response_data.get(field_name)
        message = ('Make sure that the POST request `/api/v1/games/` '
                   f'with the correct data returns {field_name}')
        if isinstance(res_data_value, list):
            assert res_data_value[0]['name'] == data[field_name][0], message
        elif field_name == 'release_date':
            assert res_data_value.split('-')[::-1] == data[field_name].split('.'), message
        else:
            assert res_data_value == data[field_name], message


@pytest.mark.asyncio
async def test_02_games_get(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        new_game: Game,
        test_app: FastAPI
):
    game_id = new_game.id
    url = test_app.url_path_for('get_game', game_id=game_id)
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/games/{game_id}` with no auth data returns 401 status'
    )
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/games/{game_id}` with auth returns 200 status'
    )
    response_data = response.json()
    field_names = game_schema.GameInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in response_data, (
            'Make sure that the GET request `/api/v1/games/{game_id}` '
            f'returns {field_name} field'
        )


@pytest.mark.asyncio
async def test_03_games_get_multi(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        test_app: FastAPI,
        new_game: Game
):
    url = test_app.url_path_for('get_games')
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/games/` w/o auth returns 401 status code'
    )
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/games/` with auth returns 200 status code'
    )
    response_data = response.json()
    assert len(response_data) == 2
    game_data = response_data.pop()
    field_names = game_schema.GameInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in game_data, (
            'Make sure that the GET request `/api/v1/games/` '
            f'with the correct data returns `{field_name}` field'
        )


@pytest.mark.asyncio
async def test_04_games_patch(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_game: Game,
        test_app: FastAPI,
        new_genre: Genre,
        new_publisher: Publisher,
        new_developer: Developer,
        new_platform: Platform
):
    data = {
        'name': 'patched_game_name',
        'price': 0.21,
        'discount': 0.22,
        'description': 'patched_game_description',
        'genres': [new_genre.name],
        'release_date': '07.05.2005',
        'publishers': [new_publisher.name],
        'developers': [new_developer.name],
        'platforms': [new_platform.name]
    }
    game_id = new_game.id
    url = test_app.url_path_for('patch_game', game_id=game_id)
    response = await auth_async_client.patch(url, json=data)
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that PATCH request to `/api/v1/games/{game_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.patch(
        url,
        json=data
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that PATCH request to `/api/v1/games/{game_id}` with admin rights returns 200 status code'
    )
    response_data = response.json()
    input_fields = data.keys()
    for field_name in input_fields:
        res_data_value = response_data.get(field_name)
        message = ('Make sure that the PATCH request `/api/v1/games/` '
                   f'with the correct data returns {field_name}')
        if isinstance(res_data_value, list):
            assert res_data_value[0]['name'] == data[field_name][0], message
        elif field_name == 'release_date':
            assert res_data_value.split('-')[::-1] == data[field_name].split('.'), message
        else:
            assert res_data_value == data[field_name], message


@pytest.mark.asyncio
async def test_05_games_delete(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_game: Game,
        test_app: FastAPI
):
    game_id = new_game.id
    url = test_app.url_path_for('delete_game', game_id=game_id)
    response = await auth_async_client.delete(url)
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that DELETE request to `/api/v1/games/{game_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.delete(
        url=url
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that DELETE request to `/api/v1/games/{game_id}` with admin rights returns 200 status code'
    )
    url = test_app.url_path_for('get_game', game_id=game_id)
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Check that GET request to `/api/v1/games/{game_id}` for deleted game_id returns 404 status code'
    )
