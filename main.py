import asyncio
from config import API_ID, API_HASH, SOURCE_CHANNEL, TARGET_CHANNEL
from client import create_client
from forwarder import setup_forwarder

async def main():
    async with create_client(API_ID, API_HASH) as client:
        await setup_forwarder(client, source=SOURCE_CHANNEL, target=TARGET_CHANNEL)
        await client.run_until_disconnected()

asyncio.run(main())