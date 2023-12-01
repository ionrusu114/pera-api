"""
This module contains the Settings class which is used to store the configuration settings of the application.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings class.

    Attributes:
    -----------
    main_url : str
        The main URL of the application.
    mysql_root_password : str
        The root password for MySQL.
    mysql_database : str
        The name of the MySQL database.
    mysql_user : str
        The username for MySQL.
    mysql_password : str
        The password for MySQL.
    mysql_host : str
        The host for MySQL.
    """
    main_url: str
    mysql_root_password: str
    mysql_database: str
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: str
    
    redis_host: str
    redis_port: int
    redis_password: str
    
    secret_auth: str
    api_key: str
    
    

settings = Settings()
