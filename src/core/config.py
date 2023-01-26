import os.path
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn, Field

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
    base_dir: str = Field(BASE_DIR, env='BASE_DIR')

    class Config:
        env_file = os.path.dirname(BASE_DIR) + '/.env'


app_settings = AppSettings()
