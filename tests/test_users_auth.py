from datetime import datetime
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from src.api.v1.endpoints.users import router as users_router
from src.api.v1.endpoints.authorization import router as auth_router


@pytest.mark.asyncio
async def test_01_users_create(test_app: FastAPI, base_url: str):
    async with AsyncClient(app=test_app, base_url=base_url) as ac:
        input_data = {
            'username': f'test_user',
            'email': f'test_user@example.com',
            'password': f'test_pass',
        }
        print('-------', test_app.url_path_for('create_user'))
        response_create = await ac.post(
            test_app.url_path_for('create_user'),
            json=input_data
        )
        print('---------')
        print(response_create.json())
        print(response_create)
        print('---------')
        assert response_create.status_code == HTTPStatus.CREATED
        response_data = response_create.json()
        input_data.pop('password')
        fields = list(input_data.keys())
        for field_name in fields:
            assert response_data.get(field_name) == input_data[field_name], (
                f'Make sure that the POST request `{test_app.url_path_for("create_user")}` '
                f' with the correct data returns {field_name}'
            )
