from http import HTTPStatus

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from src.models.models import User


@pytest.mark.asyncio
async def test_01_users_create(test_app: FastAPI, async_client: AsyncClient):
        input_data = {
            'username': f'test_user',
            'email': f'test_user@example.com',
            'password': f'test_pass',
        }
        response_create = await async_client.post(
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
                'Make sure that the POST request `/api/v1/users/{id}` '
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
        'Check that GET request to `/api/v1/users/{user_id}` with data returns 200 status'
    )
    response_data = response.json()
    fields = ['username', 'created_at', 'email', 'role']
    for field in fields:
        assert field in response_data, (
            'Make sure that the GET request `/api/v1/users/{user_id}` '
            f'with the correct data returns `{field}`'
        )


@pytest.mark.asyncio
async def test_03_users_get_multi(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        new_user: User,
        new_admin: User,
        test_app: FastAPI,
        base_url: str
):
    url = test_app.url_path_for('get_users')
    response = await async_client.get(
        url
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/users/` w/o auth returns 401 status code'
    )
    response = await auth_async_client.get(
        url
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/users/` with auth returns 200 status code'
    )
    response_data = response.json()
    assert len(response_data) == 3, (
        'Check that GET request to `/api/v1/users/` with auth returns correct data'
    )
    user_data = response_data.pop()
    fields = ['username', 'created_at', 'email', 'role']
    for field in fields:
        assert field in user_data, (
            'Make sure that the GET request `/api/v1/users/` '
            f'with the correct data returns `{field}`'
        )


@pytest.mark.asyncio
async def test_04_users_patch_admin(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_user: User,
        test_app: FastAPI

):
    data = {
        'username': 'test_patch'
    }
    user_id = new_user.id
    url = test_app.url_path_for('patch_user', user_id=user_id)
    response = await auth_async_client.patch(
        url=url,
        json=data
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that PATCH request to `/api/v1/users/{user_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.patch(
        url=url,
        json=data
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that PATCH request to `/api/v1/users/{user_id}` with admin rights returns 200 status code'
    )
    response_data = response.json()
    assert data['username'] == response_data['username'], (
        'Make sure that the get request `/api/v1/users/{user_id}` '
        'with the correct data returns username'
    )


@pytest.mark.asyncio
async def test_05_users_delete_admin(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_user: User,
        test_app: FastAPI
):
    user_id = new_user.id
    url = test_app.url_path_for('patch_user', user_id=user_id)
    response = await auth_async_client.delete(
        url=url,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that DELETE request to `/api/v1/users/{user_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.delete(
        url=url,
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that DELETE request to `/api/v1/users/{user_id}` with admin rights returns 200 status code'
    )

# TODO tests for users/me
