from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel

phone_number = '+37360361615'
client = TelegramClient(phone_number, 27284716, '1117eb19dc0b10c6f521f37e3542eaea')
client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone_number)
    client.sign_in(phone_number, input('Enter the code: '))
else:
    print('You are already logged in!')
client.disconnect()