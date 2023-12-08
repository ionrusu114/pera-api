
"""
This module contains functions for sending messages to Telegram groups and adding the message history to a database.

Functions:
- addHistory(group_id: int, account_id: int, id_group_sender: int) -> None:
    Adds the message history to the database.

- send_message(client: TelegramClient, group_name: str, group_id: int, account_id: int, id_group_sender: int, message: str) -> None:
    Sends a message to a Telegram group.

- Loop_Message(account_id: int, api_id: int, api_hash: str, phone_number: str, groups: List[Dict[int, str]], id_group_sender: int, client: TelegramClient, message: str) -> str:
    Loops through the list of groups and sends a message to each group.

- Sender(api_id: int, api_hash: str, phone_number: str, groups: List[Dict[int, str]], id_group_sender: int, id_account: int, message: str) -> str:
    Initializes the Telegram client and calls the Loop_Message function to send messages to the groups.
"""
# from telethon import TelegramClient
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from pera_fastapi.models.database import get_db
from pera_fastapi.models.schemas import GroupSelect, HistoryBase, StatusHistory
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from pera_fastapi.settings import settings
from typing import Dict, List,Annotated
from pera_fastapi.routes.history_routes import create_history

from .requests import call_create_history
import time


def send_message(
    client: TelegramClient, 
    group_name: str, 
    group_id: int, 
    account_id: int, 
    id_group_sender: int, 
    message: str):
    
    group = client.get_entity(group_name)
    try:
        client.send_message(
            entity=InputPeerChannel(group.id, group.access_hash),
            message=message,
            parse_mode='html',
            link_preview=False
        )
        history_json = {
            "id_group": group_id,
            "id_account": account_id,
            "id_group_sender": id_group_sender,
            "status": StatusHistory.success,
            "created_at": str(datetime.now()),
        }
        rs_history = call_create_history(history_json)
        print(f'rs_history: {rs_history}')
     
    except PeerFloodError:
        raise HTTPException(status_code=429, detail="Too many requests to the Telegram API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def Sender_simple(
    api_id: int, 
    api_hash: str, 
    phone_number: str, 
    groups: List[Dict[int, str]], 
    id_group_sender: int, 
    id_account: int, 
    message: str):
    
    try:
        client = TelegramClient(phone_number, api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
            client.sign_in(phone_number, input('Enter the code: '))
    
        group_name = ""
        group_id = 0      
        
        for group in groups:
            group_name = group.get('name')
            group_id = group.get('id_group')
            send_message(client, group_name, group_id, id_account, id_group_sender, message)
            time.sleep(5)
        client.disconnect()
    except Exception as e:
        print(f"An error occurred: Sender -> {e}")
        history_json = {
            "id_group": 99999,
            "id_account": id_account,
            "id_group_sender": id_group_sender,
            "status": StatusHistory.failed,
            "created_at": str(datetime.now()),
        }
        rs_history = call_create_history(history_json)
        print(f'rs_history: {rs_history}')
        client.disconnect()
        


    
    

