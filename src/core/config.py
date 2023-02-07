import os.path
from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, PostgresDsn, Field
from fastapi_mail import ConnectionConfig

from .logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    app_title: str
    database_dsn: PostgresDsn
    project_name: str
    project_host: str
    project_port: int
    secret_key: str
    algorithm: str
    token_expire_minutes: int
    reset_token_expire_minutes: int
    reset_password_auth_token_expire_minutes: int
    base_dir: str = Field(BASE_DIR, env='BASE_DIR')
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_from_name: str

    class Config:
        env_file = os.path.dirname(BASE_DIR) + '/.env'


app_settings = AppSettings()

mail_config = ConnectionConfig(
    MAIL_USERNAME=app_settings.mail_username,
    MAIL_PASSWORD=app_settings.mail_password,
    MAIL_FROM=app_settings.mail_from,
    MAIL_PORT=app_settings.mail_port,
    MAIL_SERVER=app_settings.mail_server,
    MAIL_FROM_NAME=app_settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates'
)
