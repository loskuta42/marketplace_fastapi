from http import HTTPStatus

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from src.models.models import User


@pytest.mark.asyncio
async def test_01_users_create(test_app: FastAPI, base_url: str):
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        input_data = {
            'username': f'test_user',
            'email': f'test_user@example.com',
            'password': f'test_pass',
        }
        response_create = await ac.post(
            test_app.url_path_for('create_user'),
            json=input_data
        )
        assert response_create.status_code == HTTPStatus.CREATED, (
            'Check that POST request to `/api/v1/users/` with  data returns 201 status'
        )
        response_data = response_create.json()
        input_data.pop('password')
        fields = input_data.keys()
        for field_name in fields:
            assert response_data.get(field_name) == input_data[field_name], (
                f'Make sure that the POST request `{test_app.url_path_for("create_user")}` '
                f'with the correct data returns {field_name}'
            )


@pytest.mark.asyncio
async def test_02_users_get(
        auth_async_client: AsyncClient,
        new_user: User,
        test_app: FastAPI
):
    user_id = new_user.id
    url = test_app.url_path_for('get_user', user_id=user_id)
    response = await auth_async_client.get(
        url
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/users/{id}` with data returns 201 status'
    )
    response_data = response.json()
    fields = ['username', 'created_at', 'email']
    for field in fields:
        assert field in response_data, (
            f'Make sure that the get request `{test_app.url_path_for("get_user")}` '
            f'with the correct data returns {field}'
        )


@pytest.mark.asyncio
async def test_03_users_patch():
    pass


@pytest.mark.asyncio
async def test_03_users_delete():
    pass
