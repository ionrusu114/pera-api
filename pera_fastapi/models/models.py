""" Models """
import dataclasses
from sqlalchemy import Column, Integer, String,DateTime,JSON
from pera_fastapi.models.database import Base
from datetime import datetime



class Group(Base):
    """
    A class representing a group in the system.

    Attributes:
    -----------
    id : int
        The unique identifier for the group.
    name : str
        The name of the group.
    category : str
        The category of the group.
    """
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    category = Column(String(30))


class Account(Base):
    """
    Represents a user account.

    Attributes:
        id (int): The unique identifier for the account.
        id_user (int): The unique identifier for the user associated with the account.
        phone (str): The phone number associated with the account.
        telegram_hash (str): The Telegram hash associated with the account.
        username (str): The username associated with the account.
    """    
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    telegram_hash = Column(String(30),unique=True)
    phone = Column(String(30),unique=True)
    username = Column(String(30),unique=True)
    status = Column(String(30))

class History(Base):
    """
    Represents a history record in the database.

    Attributes:
        id (int): The unique identifier for the history record.
        id_group (int): The identifier for the group associated with the history record.
        id_account (int): The identifier for the account associated with the history record.
        status (str): The status of the history record.
        created_at (str): The date and time when the history record was created.
    """
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    id_group = Column(Integer)
    id_account = Column(Integer)
    status = Column(String(30))
    created_at = Column(DateTime, default=datetime.now)

class Group_Senders(Base):
    """
    Represents a group of senders in the database.

    Attributes:
        id (int): The unique identifier for the group.
        id_account (int): The ID of the account associated with the group.
        group_list (str): A comma-separated list of sender email addresses.
        status (str): The status of the group.
        created_at (str): The date and time the group was created.
    """
    __tablename__ = 'group_senders'

    id = Column(Integer, primary_key=True)
    id_account = Column(Integer)
    group_list = Column(JSON, default=[])
    status = Column(String(30))
    delay = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    stopped_at = Column(DateTime)