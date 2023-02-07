from fastapi import APIRouter

from .endpoints.users import router as users_router
from .endpoints.authorization import router as auth_router



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
