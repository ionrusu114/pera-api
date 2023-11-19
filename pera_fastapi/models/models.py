""" Models """
import dataclasses
from sqlalchemy import Column, Integer, String,DateTime,JSON,MetaData,ForeignKey
from pera_fastapi.models.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Table,TIMESTAMP
from sqlalchemy.orm import relationship
from pera_fastapi.models.database import Base
from datetime import datetime


metadata = MetaData()
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
    metadata = metadata
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    category = Column(String(30))
    history = relationship("History", back_populates="group")


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
    metadata = metadata
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    telegram_hash = Column(String(120),unique=True)
    phone = Column(String(120),unique=True)
    username = Column(String(120),unique=True)
    status = Column(String(30))
    group_senders = relationship("Group_Senders", back_populates="account")
    history = relationship("History", back_populates="account")

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
    metadata = metadata
    id = Column(Integer, primary_key=True)
    id_group = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="history")
    id_account = Column(Integer, ForeignKey('accounts.id'))
    account = relationship("Account", back_populates="history")
    id_group_sender = Column(Integer, ForeignKey('group_senders.id'))
    group_sender = relationship("Group_Senders", back_populates="history")
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
    metadata = metadata
    id = Column(Integer, primary_key=True)
    id_account = Column(Integer, ForeignKey('accounts.id'))
    account = relationship("Account", back_populates="group_senders")
    max_executions = Column(Integer, default=2)
    message = Column(String(3600))
    group_list = Column(JSON, default=[])
    status = Column(String(30))
    delay = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    stopped_at = Column(DateTime)
    history = relationship("History", back_populates="group_sender")
    



class Role(Base):
    """
    A class representing a role in the system.

    Attributes:
    -----------
    id : int
        The unique identifier for the role.
    name : str
        The name of the role.
    permissions : dict
        The permissions associated with the role.
    """
    __tablename__ = 'role'
    metadata = metadata
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    permissions = Column(JSON, nullable=True)
    users = relationship("User", back_populates="role")

class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        email (str): The email address associated with the user.
        username (str): The username associated with the user.
        registered_at (str): The date and time when the user was registered.
        role_id (int): The identifier for the role associated with the user.
        hashed_password (str): The hashed password associated with the user.
        is_active (bool): Whether the user is active or not.
        is_superuser (bool): Whether the user is a superuser or not.
        is_verified (bool): Whether the user is verified or not.
    """
    __tablename__ = 'user'
    metadata = metadata
    id = Column(Integer, primary_key=True)
    email = Column(String(length=1024), nullable=False)
    username = Column(String(length=1024), nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey(Role.id))
    role = relationship("Role", back_populates="users")
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
