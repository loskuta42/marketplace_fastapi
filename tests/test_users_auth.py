from http import HTTPStatus
from base64 import b64decode
import re

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from src.models.models import User
from src.main import fast_mail


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
        'Make sure that the PATCH request `/api/v1/users/{user_id}` '
        'with the correct data returns username'
    )


@pytest.mark.asyncio
async def test_05_users_forget_and_reset_password(
        async_client: AsyncClient,
        test_app: FastAPI,
        new_user: User
):
    data = {
        'email': f'{new_user.email}'
    }
    url_forget_password = test_app.url_path_for('forget_password')
    fast_mail.config.SUPPRESS_SEND = 1
    with fast_mail.record_messages() as outbox:
        response = await async_client.post(url_forget_password, json=data)
        assert response.status_code == HTTPStatus.OK
        assert len(outbox) == 1
        assert outbox[0]['from'] == 'Alexey <loskuta42@yandex.ru>'
        assert outbox[0]['To'] == f'{new_user.email}'
        message = b64decode('\n'.join(outbox[0].get_payload()[0].as_string().split('\n')[4:10])).decode()
        pattern = re.compile(r'http\S+')
        token = pattern.search(message).group().split('/')[-1]
        url_confirm_res_password = test_app.url_path_for('confirm_reset_token', reset_token=token)
        response = await async_client.get(url_confirm_res_password)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert 'access_token' in response_data
        data = {
            'new_password': 'new_test_password',
            're_new_password': 'new_test_password'
        }
        url_res_password = test_app.url_path_for('reset_password')
        async_client.headers = {'Authorization': 'Bearer ' + token}
        response = await async_client.patch(url_res_password, json=data)
        assert response.status_code == HTTPStatus.OK
        wrong_data = {
            'new_password': 'new_test_password',
            're_new_password': 'new_test_password1'
        }
        response = await async_client.patch(url_res_password, json=wrong_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_06_users_delete_admin(
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


@pytest.mark.asyncio
async def test_07_users_me_get(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        test_app: FastAPI
):
    url = test_app.url_path_for('get_personal_info')
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/users/me/` w/o auth returns 401 status code'
    )
    response = await auth_async_client.get(
        url
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/users/me/` with auth returns 200 status code'
    )
    response_data = response.json()
    fields = ['username', 'created_at', 'email', 'role']
    for field in fields:
        assert field in response_data, (
            'Make sure that the GET request `/api/v1/users/me/` '
            f'with the correct data returns `{field}`'
        )


@pytest.mark.asyncio
async def test_08_users_me_patch(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        test_app: FastAPI
):
    data = {
        'username': 'test_patch'
    }
    url = test_app.url_path_for('get_personal_info')
    response = await async_client.patch(url, json=data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that PATCH request to `/api/v1/users/me/` w/o auth returns 401 status code'
    )
    response = await auth_async_client.patch(url, json=data)
    response_data = response.json()
    fields = ['username', 'created_at', 'email', 'role']
    for field in fields:
        assert field in response_data, (
            'Make sure that the PATCH request `/api/v1/users/me/` '
            f'with the correct data returns `{field}`'
        )
    assert data['username'] == response_data['username'], (
        'Make sure that the PATCH request `/api/v1/users/me/` '
        'with the correct data returns username'
    )
