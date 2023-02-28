from http import HTTPStatus

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.models.models import Genre


@pytest.mark.asyncio
async def test_01_genre_create(
        test_app: FastAPI,
        auth_async_client: AsyncClient,
        auth_async_admin_client: AsyncClient,
        new_genre: Genre
):
    input_data = {
        'name': 'created_genre',
        'description': 'created_genre_description'
    }
    url = test_app.url_path_for('create_genre')
    # response = await auth_async_client.post(
    #     url,
    #     json=input_data
    # )
    # assert response.status_code == HTTPStatus.FORBIDDEN, (
    #     'Check that POST request to `/api/v1/genres/` by not admin return 403 status code'
    # )
    # response = await auth_async_admin_client.post(
    #     url,
    # )
    # assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    response = await auth_async_admin_client.post(
        url,
        json=input_data
    )
    assert response.status_code == HTTPStatus.CREATED
    # response_data = response_create.json()

