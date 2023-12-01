"""
This module contains a Celery task that sends messages to a list of groups periodically.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List,Annotated
from fastapi import APIRouter,BackgroundTasks, Depends,HTTPException, status,Request,Response
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from celery.utils.log import get_task_logger

from pera_fastapi.models.schemas import GroupSelect,HistoryBase,StatusHistory, GroupsSendersSelectBase,StatusGroupSenders
from pera_fastapi.settings import settings
from pera_fastapi.models.database import get_db,engine
from .SendMessToChat import Sender
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session
from pera_fastapi.routes.history_routes import create_history
from pera_fastapi.routes.group_senders_router import update_group_senders
from pera_fastapi.models.schemas import GroupsSendersSelectBase

from sqlalchemy.orm import sessionmaker
from celery.schedules import crontab
# cSpell:ignore sessionmaker
import redis
from redis import asyncio as aioredis
import json
from celery import Task, shared_task
from sqlalchemy.ext.asyncio import async_sessionmaker
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor


DBD = Annotated[Session, Depends(get_db)]

redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0"
celery = Celery("tasks", broker=redis_url,backend=redis_url)

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)
celery.conf.broker_connection_retry_on_startup = True

URL_DATABASE = 'mysql+aiomysql://{}:{}@{}:3306/{}'.format(settings.mysql_user,settings.mysql_password,settings.mysql_host,settings.mysql_database)

engine_async = create_async_engine(URL_DATABASE)  # replace with your actual database connection string

class DatabaseTask(Task):
    _session = None

    @property
    def session(self):
        if self._session is None:
            self._session = AsyncSession(engine_async)
        return self._session

@shared_task(bind=True, base=DatabaseTask, name="tasks.send_messages")
def send_messages(
    self,
    account: List,
    max_executions: int,
    message: str,
    group_list: List[Dict[int, str]], 
    id_group_senders: int,
    period: int,
    ):
 
    api_id, api_hash, id_account, phone_number = account.get('telegram_id'), account.get('telegram_hash'), account.get('id'), account.get('phone')
  
    groups = group_list
    id_group_sender = id_group_senders
    
    async def main():
        loop = asyncio.get_event_loop()
        session = AsyncSession(engine_async, future=loop.create_future())
        try:
            await Sender(
                api_id, 
                api_hash, 
                phone_number, 
                groups, 
                id_group_sender, 
                id_account,
                message,
            )

            if max_executions <= 1:
                # Update the status of the group of senders
                group_senders = GroupsSendersSelectBase(
                    id_account=id_account,
                    max_executions=max_executions,
                    message=message,
                    group_list=group_list,
                    status=StatusGroupSenders.finished,
                    delay=12,
                    created_at=datetime.now(),
                )
                group_senders_dict = group_senders.dict()
                
                update = await update_group_senders(id_group_senders, group_senders, session)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if not loop.is_closed():
                await session.close()

    async def run_main_periodically():
        nonlocal max_executions
        while max_executions >= 1:
            await main()
            # await asyncio.sleep(period*60*60) # 2 hours sleep
            await asyncio.sleep(period) # 2 hours sleep
            max_executions -= 1

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(run_main_periodically())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleaning up...")
        # Cancel all running tasks
        for task in asyncio.all_tasks(loop):
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass

        # Stop the event loop
        loop.stop()
        while loop.is_running():
            pass

        # Close the event loop
        loop.close()
        print("Loop closed")
        print(f'Task finished {id_group_senders}')
        
