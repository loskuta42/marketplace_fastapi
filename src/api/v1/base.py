from fastapi import APIRouter

from .endpoints.users import router as users_router
from .endpoints.authorization import router as auth_router
from .endpoints.genres import router as genres_router
from .endpoints.publishers import router as publishers_router
from .endpoints.developers import router as developers_router
from .endpoints.platforms import router as platforms_router



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

api_router.include_router(
    publishers_router,
    prefix='/publishers',
    tags=['publishers']
)

api_router.include_router(
    developers_router,
    prefix='/developers',
    tags=['developers']
)

api_router.include_router(
    platforms_router,
    prefix='/platforms',
    tags=['platforms']
)
