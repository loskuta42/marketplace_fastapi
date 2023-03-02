from http import HTTPStatus

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.models.models import Genre
from src.schemas import genres as genre_schema


@pytest.mark.asyncio
async def test_01_genres_create(
        test_app: FastAPI,
        auth_async_client: AsyncClient,
        auth_async_admin_client: AsyncClient,
):
    input_data = {
        'name': 'created_genre',
        'description': 'created_genre_description'
    }
    url = test_app.url_path_for('create_genre')
    response = await auth_async_client.post(
        url,
        json=input_data
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that POST request to `/api/v1/genres/` by not admin return 403 status code'
    )
    response = await auth_async_admin_client.post(
        url,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    response = await auth_async_admin_client.post(
        url,
        json=input_data
    )
    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    field_names = genre_schema.GenreInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in response_data, (
            'Make sure that the POST request `/api/v1/genres/` '
            f'returns {field_name} field'
        )

    input_fields = input_data.keys()
    for field_name in input_fields:
        assert response_data.get(field_name) == input_data[field_name], (
            'Make sure that the POST request `/api/v1/genres/` '
            f'with the correct data returns {field_name}'
        )


@pytest.mark.asyncio
async def test_02_genres_get(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        new_genre: Genre,
        test_app: FastAPI
):
    genre_id = new_genre.id
    url = test_app.url_path_for('get_genre', genre_id=genre_id)
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/genres/{genre_id}` with no auth data returns 401 status'
    )
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/genres/{genre_id}` with auth returns 200 status'
    )
    response_data = response.json()
    field_names = genre_schema.GenreInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in response_data, (
            'Make sure that the GET request `/api/v1/genres/{genre_id}` '
            f'returns {field_name} field'
        )


@pytest.mark.asyncio
async def test_03_genres_get_multi(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        test_app: FastAPI,
        new_genre: Genre
):
    url = test_app.url_path_for('get_genres')
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/genres/` w/o auth returns 401 status code'
    )
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/genres/` with auth returns 200 status code'
    )
    response_data = response.json()
    assert len(response_data) == 2
    genre_data = response_data.pop()
    field_names = genre_schema.GenreInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in genre_data, (
            'Make sure that the GET request `/api/v1/genres/` '
            f'with the correct data returns `{field_name}` field'
        )


@pytest.mark.asyncio
async def test_04_genres_patch(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_genre: Genre,
        test_app: FastAPI
):
    data = {
        'name': 'patched_name',
        'description': 'patched_description'
    }
    genre_id = new_genre.id
    url = test_app.url_path_for('patch_genre', genre_id=genre_id)
    response = await auth_async_client.patch(url, json=data)
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that PATCH request to `/api/v1/genres/{genre_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.patch(
        url,
        json=data
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that PATCH request to `/api/v1/genres/{genre_id}` with admin rights returns 200 status code'
    )
    response_data = response.json()
    for field in data:
        assert data[field] == response_data[field], (
            'Make sure that the PATCH request `/api/v1/genres/{genre_id}` '
            f'with the correct data returns {field} field'
        )
    url = test_app.url_path_for('get_genre', genre_id=genre_id)
    response = await auth_async_admin_client.get(url)
    response_data = response.json()
    for field in data:
        assert data[field] == response_data[field], (
            'Make sure that the PATCH request `/api/v1/genres/{genre_id}` '
            f'actually patch {field} field'
        )

@pytest.mark.asyncio
async def test_05_genres_delete(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_genre: Genre,
        test_app: FastAPI
):
    genre_id = new_genre.id
    url = test_app.url_path_for('delete_genre', genre_id=genre_id)
    response = await auth_async_client.delete(url)
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that DELETE request to `/api/v1/genres/{genre_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.delete(
        url=url
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that DELETE request to `/api/v1/genres/{genre_id}` with admin rights returns 200 status code'
    )
    url = test_app.url_path_for('get_genre', genre_id=genre_id)
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Check that GET request to `/api/v1/genres/{genre_id}` for deleted genre_id returns 404 status code'
    )