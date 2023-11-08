from sqlalchemy import Boolean, Column, Integer, String, BigInteger, Float,Numeric,DateTime
from .database import Base
import datetime

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    category = Column(String(30))
  