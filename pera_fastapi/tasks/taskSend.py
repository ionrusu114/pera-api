import asyncio
from datetime import timedelta
from typing import Dict, List

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from celery.utils.log import get_task_logger

from pera_fastapi.models.schemas import GroupSelect
from pera_fastapi.models.settings import settings
from pera_fastapi.models.database import get_db
from .SendMessToChat import Sender
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from celery.schedules import crontab
# cSpell:ignore sessionmaker
import redis
from redis import asyncio as aioredis
import json

redis_url = "redis://:leonidas1121@localhost:6379/0"
celery = Celery("tasks", broker=redis_url,backend=redis_url)

# r = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
r = redis.Redis(host='localhost', port=6379, db=0, password='leonidas1121')
celery.conf.broker_connection_retry_on_startup = True

logger = get_task_logger(__name__)

# Define your arguments here
account = []
max_executions = 0
message = ""
group_list = []
id_group_senders = 0
period = 12

celery.conf.beat_schedule = {
    "send-messages-every-20-seconds": {
        "task": "tasks.send_messages",
        "schedule": timedelta(seconds=20),
        "args": (account, max_executions, message, group_list, id_group_senders, period),
        "kwargs": {},
    },
}

@celery.task(bind=True,name="tasks.send_messages")
def send_messages(
    self,
    account: List,
    max_executions: int,
    message: str,
    group_list: List[Dict[int, str]], 
    id_group_senders: int,
    period: int,
    ):

    saved_data = r.get('saved_data')
    if saved_data:
        saved_data = json.loads(saved_data)
        print(f' saved_data: {saved_data}')
        account = saved_data.get('account', account)
        max_executions = saved_data.get('max_executions', max_executions)
        message = saved_data.get('message', message)
        group_list = saved_data.get('group_list', group_list)
        id_group_senders = saved_data.get('id_group_senders', id_group_senders)
        period = saved_data.get('period', period)
        
    if not account:
        return
    
    if max_executions == 0:
        r.delete('saved_data')
        return 
    
    print(f'max-executions: {max_executions}')
    max_executions -= 1    
    
    

    api_id, api_hash, id_account, phone_number = account.get('telegram_id'), account.get('telegram_hash'), account.get('id'), account.get('phone')
  
    groups = group_list
    id_group_sender = id_group_senders
    
    async def main():
        await Sender(
            api_id, 
            api_hash, 
            phone_number, 
            groups, 
            id_group_sender, 
            id_account,
            message,
            )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    
    # Save data for next execution
    # Save data to Redis for next execution
    saved_data = {
        'account': account,
        'max_executions': max_executions,
        'message': message,
        'group_list': group_list,
        'id_group_senders': id_group_senders,
        'period': period,
    }
    r.set('saved_data', json.dumps(saved_data))

    
