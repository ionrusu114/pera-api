"""Settings"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Settings class"""
    main_url: str
    mysql_root_password: str
    mysql_database: str
    mysql_user: str
    mysql_password: str
    mysql_host: str

settings = Settings()
