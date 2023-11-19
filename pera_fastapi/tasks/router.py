"""
This module contains the API router for handling tasks related to sending messages to a group of recipients.

Functions:
- run_sender_messages: An endpoint to add a task to send messages to a group of recipients.
"""
from fastapi import APIRouter,BackgroundTasks, Depends,HTTPException, status,Request,Response
from typing import Dict, List,Annotated
from fastapi_cache.decorator import cache
import importlib
from pera_fastapi.auth.database import User
from pera_fastapi.models.schemas import Group_SendersBase,GroupsSendersSelectBase
from pera_fastapi.models.database import get_db
from pera_fastapi.routes.account_router import get_account
from pera_fastapi.routes.group_senders_router import create_group_senders
from sqlalchemy.future import select
from pera_fastapi.models import models
from sqlalchemy.orm import Session
from .tasks import send_messages
from fastapi.responses import JSONResponse
import logging


DBD = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/api/telegram/tasks", tags=["tasks"])

@router.post("/send",status_code=status.HTTP_201_CREATED)
async def run_sender_messages(
        # max_executions: int,
        # message: str,
        group_senders: GroupsSendersSelectBase,
        db: DBD,
    ):
    """
    Endpoint to add a task to send messages to a group of recipients.
    
    Args:
    - group_senders (GroupsSendersSelectBase): A Pydantic model representing the group of recipients and the message to be sent.
    - db (DBD): A database connection object.
    
    Returns:
    - JSONResponse: A JSON response indicating whether the task was successfully added or not.
    """
    async def cached_create_group_senders(group_senders, db):
        return await create_group_senders(group_senders, db)

    created_group_senders = await cached_create_group_senders(group_senders, db)
    id_group_senders = created_group_senders.get('id')
    
    async def cached_get_account(id_account, db):
        return await get_account(id_account, db)
    account = await cached_get_account(group_senders.id_account, db)
    
    def serialize_model_instance(instance):
        data = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
        return data
    
    account_dict = serialize_model_instance(account)
    group_select_dict = [group.dict() for group in group_senders.group_list]
    max_executions = group_senders.max_executions
    message = group_senders.message
    
    send_messages.delay(
        account_dict,
        max_executions,
        message,
        group_select_dict,
        id_group_senders,
        group_senders.delay,        
    )
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Success add task"})
