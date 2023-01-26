from fastapi import APIRouter

from .endpoints import authorization, users


api_router = APIRouter()


api_router.include_router(
    users.router,
    prefix='/users',
    tags=['users']
)

api_router.include_router(
    authorization.router,
    prefix='/authorization',
    tags=['authorization']
)
