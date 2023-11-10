""" Database """
import dataclasses
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .settings import settings

URL_DATABASE = 'mysql+pymysql://{}:{}@{}:3306/{}'.format(settings.mysql_user,settings.mysql_password,settings.mysql_host,settings.mysql_database)
# URL_DATABASE = 'mysql+pymysql://peradmin:wQlG5unrYTLT9cTONHcg@localhost:3306/pera-api'

engine = create_engine(URL_DATABASE)

SesssionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

Base = declarative_base()

def get_db():
    """ get DB function """
    db = SesssionLocal()
    try:
        yield db
    finally:
        db.close()
