from dotenv import load_dotenv
import os
from pera_fastapi.settings import  settings

load_dotenv()

# MYSQL_HOST = os.environ.get("MYSQL_HOST")
# MYSQL_USER = os.environ.get("MYSQL_USER")
# MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
# MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
# MYSQL_PORT = os.environ.get("MYSQL_PORT")

# REDIS_HOST = os.environ.get("REDIS_HOST")
# REDIS_PORT = os.environ.get("REDIS_PORT")
# REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")


# SECRET_AUTH = os.environ.get("SECRET_AUTH")

MYSQL_HOST = settings.mysql_host
MYSQL_USER = settings.mysql_user
MYSQL_PASSWORD = settings.mysql_password
MYSQL_DATABASE = settings.mysql_database
MYSQL_PORT = settings.mysql_port

# REDIS_HOST = settings.redis_host
# REDIS_PORT = settings.redis_port
# REDIS_PASSWORD = settings.redis_password

SECRET_AUTH = settings.secret_auth

