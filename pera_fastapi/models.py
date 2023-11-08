""" Models """
import dataclasses
from sqlalchemy import Column, Integer, String
from .database import Base

# @dataclasses.dataclass
class Group(Base):
    """ Group model class"""
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    category = Column(String(30))
  