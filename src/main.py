import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.core.config import app_settings


app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    swagger_ui_oauth2_redirect_url='authorization/token'
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
