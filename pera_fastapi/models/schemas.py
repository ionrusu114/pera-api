from typing import List,Tuple,Optional
from pydantic import BaseModel,Field
from datetime import datetime
from enum import Enum

class GroupBase(BaseModel):
    """
    Represents a group of users.

    Attributes:
        name (str): The name of the group.
        category (str, optional): The category of the group. Defaults to "MD".
    """
    name: str
    category: str = Field(default="MD")


class StatusAccount(str, Enum):
    """
    Enum class representing the status of a task.
    """
    active = "active"
    inactive = "inactive"

class AccountBase(BaseModel):
    """
    Represents a user account.

    Attributes:
        telegram_id (int): The Telegram ID of the account.
        telegram_hash (str): The Telegram hash of the account.
        phone (str): The phone number of the account.
        username (str): The username of the account.
    """
    telegram_id: int
    telegram_hash: str
    phone: str
    username: str
    status: str = Field(default=StatusAccount.inactive, description="The status of the account. Can be 'inactive', 'active'.")

class StatusHistory(str, Enum):
    """
    Enum class representing the status of a task.
    """
    pending = "pending"
    success = "success"
    failed = "failed"

class HistoryBase(BaseModel):
    """
    Represents a history record.

    Attributes:
        id_group (int): The ID of the group associated with the history record.
        id_account (int): The ID of the account associated with the history record.
        status (str): The status of the history record.
        created_at (str): The date and time when the history record was created.
    """
    id_group: int
    id_account: int
    status: str = Field(default=StatusHistory.pending, description="The status of the history record. Can be 'pending', 'success', 'failed'.")
    created_at: datetime = Field(default=datetime.now(), description="The date and time when the history record was created.")

class StatusGroupSenders(str, Enum):
    """
    Enum class representing the status of a task.
    """
    active = "active"
    inactive = "inactive"
    pending = "pending"

class GroupSelect(BaseModel):
    """
    Represents a group of senders.

    Attributes:
        id_account (int): The ID of the account associated with the group.
        id_group (int): The ID of the group associated with the group.
    """
    id_group: int
    name: str
    category: str = Field(default="MD")
    
class Group_SendersBase(BaseModel):
    """
    Represents a group of senders.

    Attributes:
        id_account (int): The ID of the account associated with the group.
        id_group (int): The ID of the group associated with the group.
    """
    id_account: int
    group_list: List[GroupSelect] = Field(default=[], description="The list of groups associated with the group of senders.")
    status: str = Field(default=StatusGroupSenders.pending, description="The status of the group of senders. Can be 'pending', 'active', 'inactive'.")
    delay: int = Field(default=12, description="The delay between messages in hours.")
    created_at: datetime = Field(default=datetime.now(), description="The date and time when the group of senders was created.")
    # stopped_at: Optional[datetime] = Field(default=None, description="The date and time when the group of senders was stopped.")




