from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'mysql+pymysql://peradmin:wQlG5unrYTLT9cTONHcg@localhost:3306/pera-api'

engine = create_engine(URL_DATABASE)

SesssionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

Base = declarative_base()