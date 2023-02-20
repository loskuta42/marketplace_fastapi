from fastapi import APIRouter

from .endpoints.users import router as users_router
from .endpoints.authorization import router as auth_router
from .endpoints.genres import router as genres_router


api_router = APIRouter()

api_router.include_router(
    users_router,
    prefix='/users',
    tags=['users']
)

api_router.include_router(
    auth_router,
    prefix='/authorization',
    tags=['authorization']
)

api_router.include_router(
    genres_router,
    prefix='/genres',
    tags=['genres']
)
