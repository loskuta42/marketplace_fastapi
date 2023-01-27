from http import HTTPStatus

import pytest
from httpx import AsyncClient
from fastapi import FastAPI


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
            'Check that POST request to `/api/v1/users/` with wrong data returns 201 status'
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
async def test_02_users_get(test_app: FastAPI, base_url: str):
    # TODO
    pass
