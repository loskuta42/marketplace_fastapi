import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_mail import FastMail

from src.core.config import app_settings, mail_config
from src.api.v1 import base


app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    swagger_ui_oauth2_redirect_url='/authorization/token'
)

fast_mail = FastMail(config=mail_config)

app.include_router(base.api_router, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
