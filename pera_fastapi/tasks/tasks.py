"""
This module contains a Celery task that sends messages to a list of groups periodically.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Request, Response
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from celery.utils.log import get_task_logger
from enum import Enum

from pera_fastapi.models.schemas import GroupSelect, HistoryBase, StatusHistory, GroupsSendersSelectBase, StatusGroupSenders, StatusAccount, TaskUpdateStatusBase, StatusTasks
from pera_fastapi.settings import settings
from pera_fastapi.models.database import get_db, engine
from .SendMessToChat import Sender
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session
from pera_fastapi.routes.history_routes import create_history
from pera_fastapi.routes.group_router import get_all_groups_count
from pera_fastapi.routes.group_senders_router import update_group_senders
from pera_fastapi.routes.tasks_router import update_task_work,get_task_by_group_sender
from pera_fastapi.routes.account_router import update_account_status
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
import time
import requests
from sqlalchemy import text

from .requests import call_fastapi_endpoint_test_gwt_account,call_fastapi_update_group_senders,call_update_account_status,call_update_task_work

from .SenderToGroups import Sender_simple



DBD = Annotated[Session, Depends(get_db)]

redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0"
celery = Celery("tasks", broker=redis_url, backend=redis_url)

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)
celery.conf.broker_connection_retry_on_startup = True

URL_DATABASE = 'mysql+aiomysql://{}:{}@{}:3306/{}'.format(settings.mysql_user, settings.mysql_password, settings.mysql_host, settings.mysql_database)

engine_async = create_async_engine(URL_DATABASE)  # replace with your actual database connection string


class DatabaseTask(Task):
    _session = None

    @property
    def session(self):
        if self._session is None:
            self._session = AsyncSession(engine_async)
        return self._session



@shared_task(bind=True,name="tasks.send_messages")
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
    
    data_acc = call_fastapi_endpoint_test_gwt_account(id_account)
    
    print(f'Data account: {data_acc}')
    
    # session = await self.session

    async def main():
        loop = asyncio.get_event_loop()
       
        try:
            # loop = asyncio.get_event_loop()
            try:
                time.sleep(5)
                await Sender(
                    api_id,
                    api_hash,
                    phone_number,
                    groups,
                    id_group_sender,
                    id_account,
                    message,
                    # session,
                )
            except Exception as e:
                print(f"An error occurred: Sender -> {e}")
            
            
            if max_executions <= 1:
                # Update the status of the group of senders
                
                data = {
                    "id_account": id_account,
                    "max_executions": max_executions,
                    "message": "message",
                    "group_list": group_list,
                    "status": StatusGroupSenders.finished,
                    "delay": period,
                    "created_at": str(datetime.now()),
                }

                rs_gs = call_fastapi_update_group_senders(id_group_senders, data)
                print(f'Update group senders: {rs_gs}')
                
                rs_ac = call_update_account_status(id_account, StatusAccount.inactive)
                print(f'Update account status: {rs_ac}')
                status_task = {
                    "status": StatusTasks.success,
                }
                rs_task = call_update_task_work(id_group_senders, status_task)
                print(f'Update task status: {rs_task}')
                
                
        except Exception as e:
            print(f"An error occurred: send message {e}")
            
        # finally:
            # await session.close()

    async def run_main_periodically():
        nonlocal max_executions
        
        while max_executions >= 1:
            await main()
            await asyncio.sleep(5)
            
            # await asyncio.sleep(period*60*60) # 2 hours sleep
            await asyncio.sleep(period)
            max_executions -= 1

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop = asyncio.get_event_loop()
    # session = AsyncSession(engine_async)
    try:
        tasks = asyncio.gather(*[loop.create_task(run_main_periodically()) for _ in range(max_executions)])
        loop.run_until_complete(tasks)
        
    except Exception as e:
        print(f"An error occurred: after run {e}")
    finally:
        print("Cleaning up...")
        # Cancel all running tasks
        for task in asyncio.all_tasks(loop):
            task.cancel()
        # Close the event loop
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        print("Loop closed")
        print(f'Task finished {id_group_senders}')
    
    print(f'Task finished {loop.is_closed()}')
    
    
    
@shared_task(bind=True, name="tasks.send_messages_simple")
def send_messages_simple(
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
    
    try:
        while max_executions >= 1:
            try:
                time.sleep(5)
                Sender_simple(
                    api_id,
                    api_hash,
                    phone_number,
                    groups,
                    id_group_sender,
                    id_account,
                    message,
                )
                

            except Exception as e:
                print(f"An error occurred: Sender -> {e}")
            finally:
                time.sleep(period)
                max_executions -= 1
                print(f'Message send | max-executions   {max_executions}')
    except Exception as e:
        print(f"An error occurred: send messages {e}")
    finally:
        data = {
            "id_account": id_account,
            "max_executions": max_executions,
            "message": "message",
            "group_list": group_list,
            "status": StatusGroupSenders.finished,
            "delay": period,
            "created_at": str(datetime.now()),
        }

        rs_gs = call_fastapi_update_group_senders(id_group_senders, data)
        print(f'Update group senders: {rs_gs}')
        
        rs_ac = call_update_account_status(id_account, StatusAccount.inactive)
        print(f'Update account status: {rs_ac}')
        status_task = {
            "status": StatusTasks.success,
        }
        rs_task = call_update_task_work(id_group_senders, status_task)
        print(f'Update task status: {rs_task}')
        
        
        print(f'Task finished {id_group_senders}')
    
        
