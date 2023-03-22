from http import HTTPStatus

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.models.models import Developer
from src.schemas import pub_dev as developer_schema


@pytest.mark.asyncio
async def test_01_developer_create(
        test_app: FastAPI,
        auth_async_client: AsyncClient,
        auth_async_admin_client: AsyncClient,
):
    input_data = {
        'name': 'created_developer',
        'country': 'created_country'
    }
    url = test_app.url_path_for('create_developer')
    response = await auth_async_client.post(
        url,
        json=input_data
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that POST request to `/api/v1/developers/` by not admin return 403 status code'
    )
    response = await auth_async_admin_client.post(
        url
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'Check that POST request to `/api/v1/developers/` with no body and with admin rights return 422 status code'
    )
    response = await auth_async_admin_client.post(
        url,
        json=input_data
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Check that POST request to `/api/v1/developers/` with admin rights return 201 status code'
    )
    response_data = response.json()
    field_names = developer_schema.PubDevInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in response_data, (
            'Make sure that the POST request `/api/v1/developers/` '
            f'returns {field_name} field'
        )

    input_fields = input_data.keys()
    for field_name in input_fields:
        assert response_data.get(field_name) == input_data[field_name], (
            'Make sure that the POST request `/api/v1/developers/` '
            f'with the correct data returns {field_name}'
        )


@pytest.mark.asyncio
async def test_02_developers_get(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        new_developer: Developer,
        test_app: FastAPI
):
    developer_id = new_developer.id
    url = test_app.url_path_for('get_developer', developer_id=developer_id)
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/developers/{developer_id}` with no auth data returns 401 status'
    )
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/developers/{developer_id}` with auth returns 200 status'
    )
    response_data = response.json()
    field_names = developer_schema.PubDevInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in response_data, (
            'Make sure that the GET request `/api/v1/developers/{developer_id}` '
            f'returns {field_name} field'
        )


@pytest.mark.asyncio
async def test_03_developers_get_multi(
        auth_async_client: AsyncClient,
        async_client: AsyncClient,
        test_app: FastAPI,
        new_developer: Developer
):
    url = test_app.url_path_for('get_developers')
    response = await async_client.get(url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Check that GET request to `/api/v1/developers/` w/o auth returns 401 status code'
    )
    response = await auth_async_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Check that GET request to `/api/v1/developers/` with auth returns 200 status code'
    )
    response_data = response.json()
    assert len(response_data) == 2
    developer_data = response_data.pop()
    field_names = developer_schema.PubDevInDB.__fields__.keys()
    for field_name in field_names:
        assert field_name in developer_data, (
            'Make sure that the GET request `/api/v1/developers/` '
            f'with the correct data returns `{field_name}` field'
        )


@pytest.mark.asyncio
async def test_04_developers_patch(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_developer: Developer,
        test_app: FastAPI
):
    data = {
        'name': 'patched_name',
        'country': 'patched_country'
    }
    developer_id = new_developer.id
    url = test_app.url_path_for('patch_developer', developer_id=developer_id)
    response = await auth_async_client.patch(
        url,
        json=data
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that PATCH request to `/api/v1/developers/{developer_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.patch(
        url,
        json=data
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that PATCH request to `/api/v1/developers/{developer_id}` with admin rights returns 200 status code'
    )
    response_data = response.json()
    for field in data:
        assert data[field] == response_data[field], (
            'Make sure that the PATCH request `/api/v1/developers/{developer_id}` '
            f'with the correct data returns {field} field'
        )
    url = test_app.url_path_for('get_developer', developer_id=developer_id)
    response = await auth_async_admin_client.get(url)
    response_data = response.json()
    for field in data:
        assert data[field] == response_data[field], (
            'Make sure that the PATCH request `/api/v1/developers/{developer_id}` '
            f'actually patch {field} field'
        )


@pytest.mark.asyncio
async def test_05_developers_delete(
        auth_async_admin_client: AsyncClient,
        auth_async_client: AsyncClient,
        new_developer: Developer,
        test_app: FastAPI
):
    developer_id = new_developer.id
    url = test_app.url_path_for('delete_developer', developer_id=developer_id)
    response = await auth_async_client.delete(url)
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Check that DELETE request to `/api/v1/developers/{developer_id}` w/o admin rights returns 403 status code'
    )
    response = await auth_async_admin_client.delete(
        url
    )
    assert response.status_code == HTTPStatus.OK, (
        'Check that DELETE request to `/api/v1/developers/{developer_id}` with admin rights returns 200 status code'
    )
    url = test_app.url_path_for('get_developer', developer_id=developer_id)
    response = await auth_async_client.get(
        url
    )
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Check that GET request to `/api/v1/developers/{developer_id}` for deleted developer_id returns 404 status '
        'code'
    )
