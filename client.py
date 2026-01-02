from telethon.sync import TelegramClient

def create_client(api_id, api_hash):
    return TelegramClient('session', api_id, api_hash)