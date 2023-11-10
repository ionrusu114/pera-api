
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel
import time

# Replace the values below with your own API ID, API hash, and phone number
api_id = 21053751
api_hash = '1fd3190da89adf34db18acf2a1e4fc30'
phone_number = '+40784112735'

# Replace the value below with the name of the group you want to send a message to
group_name = 'myFriendPublicGroup'

# Connect to the Telegram client

groups = [{'id': 1, 'name': 'myFriendPublicGroup'}, {'id': 2, 'name': 'tGroupN'}]

async def send_message(client: TelegramClient, group_name: str):
    group = await client.get_entity(group_name)
    try:
        await client(SendMessageRequest(
            peer=InputPeerChannel(group.id, group.access_hash),
            message='test message'
        ))
    except PeerFloodError:
        print('Error: Too many requests')

async def Loop_Messages(api_id: int, api_hash: str, phone_number: str, groups: list,client: TelegramClient):
    
    client = TelegramClient('session-{}'.format(phone_number), api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))
    for group in groups:
        # print(group.get('name'))
        await send_message(client,group.get('name'))
        time.sleep(5)

def main(api_id: int, api_hash: str, phone_number: str, groups: list):
    client = TelegramClient('session-{}'.format(phone_number), api_id, api_hash)
    client.loop.run_until_complete(Loop_Messages(api_id, api_hash, phone_number, groups,client))

main(api_id, api_hash, phone_number, groups)
# Loop_Messages(api_id, api_hash, phone_number, groups)

