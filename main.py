import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import accounts, channels, links, forwarding
from logger import logger


async def main():
    logger.info("Запуск бота")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(accounts.router)
    dp.include_router(channels.router)
    dp.include_router(links.router)
    dp.include_router(forwarding.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())