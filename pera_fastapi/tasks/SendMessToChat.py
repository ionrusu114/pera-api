
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
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from pera_fastapi.models.database import get_db
from pera_fastapi.models.schemas import GroupSelect, HistoryBase, StatusHistory
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from pera_fastapi.settings import settings
from typing import Dict, List,Annotated
from pera_fastapi.routes.history_routes import create_history

URL_DATABASE = 'mysql+aiomysql://{}:{}@{}:3306/{}'.format(settings.mysql_user,settings.mysql_password,settings.mysql_host,settings.mysql_database)
engine_async = create_async_engine(URL_DATABASE)

async def addHistory(group_id, account_id, id_group_sender):
    """
    Adds a new history record to the database.

    Args:
        group_id (int): The ID of the group.
        account_id (int): The ID of the account.
        id_group_sender (int): The ID of the group sender.

    Raises:
        HTTPException: If an error occurs while committing the transaction.

    Returns:
        None
    """
    session = AsyncSession(engine_async)
    try:
        history = HistoryBase(
            id_group=group_id,
            id_account=account_id,
            id_group_sender=id_group_sender,
            status=StatusHistory.success,
            created_at=datetime.now(),
        )
        try:
            await create_history(history, session)
        except Exception as e:
            raise HTTPException(status_code=400, detail="An error occurred while committing the transaction.") from e
    finally:
        await session.close()

async def send_message(client: TelegramClient, group_name: str, group_id: int, account_id: int, id_group_sender: int, message: str):
    """
    Sends a message to a Telegram group using the given TelegramClient instance.

    Args:
        client (TelegramClient): The TelegramClient instance to use for sending the message.
        group_name (str): The name of the Telegram group to send the message to.
        group_id (int): The ID of the Telegram group to send the message to.
        account_id (int): The ID of the Telegram account that is sending the message.
        id_group_sender (int): The ID of the group sender.
        message (str): The message to send.

    Raises:
        PeerFloodError: If too many requests are made to the Telegram API.

    Returns:
        None
    """
    group = await client.get_entity(group_name)
    try:
        await client(SendMessageRequest(peer=InputPeerChannel(group.id, group.access_hash), message=message))
        await addHistory(group_id, account_id, id_group_sender)
        print('Message sent to', group_name)
    except PeerFloodError:
        print('Error: Too many requests')

async def Loop_Message(account_id: int, api_id: int, api_hash: str, phone_number: str, groups: List[Dict[int, str]], id_group_sender: int, client: TelegramClient, message: str):
    """
    Sends a message to multiple Telegram groups, with a delay of 5 seconds between each message.

    Args:
        account_id (int): The ID of the Telegram account.
        api_id (int): The API ID of the Telegram account.
        api_hash (str): The API hash of the Telegram account.
        phone_number (str): The phone number of the Telegram account.
        groups (List[Dict[int, str]]): A list of dictionaries containing the name and ID of each group to send the message to.
        id_group_sender (int): The ID of the group sending the message.
        client (TelegramClient): The Telegram client object.
        message (str): The message to send.

    Returns:
        None
    """
    await client.connect()
    if not await client.is_user_authorized():
        code = await client.send_code_request(phone_number)
        print(f'Code: {code}')
        await client.sign_in(phone_number, input('Enter the code: '))
    for group in groups:
        print(f'group: {group}')
        await send_message(client, group.get('name'), group.get('id_group'), account_id, id_group_sender, message)
        await asyncio.sleep(5)

async def Sender(api_id: int, api_hash: str, phone_number: str, groups: List[Dict[int, str]], id_group_sender: int, id_account: int, message: str):
    """
    Sends a message to a list of Telegram groups using the specified Telegram API credentials.

    Args:
        api_id (int): The Telegram API ID.
        api_hash (str): The Telegram API hash.
        phone_number (str): The phone number associated with the Telegram account.
        groups (List[Dict[int, str]]): A list of dictionaries containing the ID and title of each group to send the message to.
        id_group_sender (int): The ID of the group that the message is being sent from.
        id_account (int): The ID of the Telegram account associated with the API credentials.
        message (str): The message to send to the specified groups.

    Returns:
        str: A string indicating the success of the message sending process.
    """
    client = TelegramClient(f'{phone_number}.session', api_id, api_hash)
    try:
        await Loop_Message(id_account, api_id, api_hash, phone_number, groups, id_group_sender, client, message)
    finally:
        await client.disconnect()
    return "Success"


