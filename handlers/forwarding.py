from aiogram import Router, F
from aiogram.types import Message
from storage import storage
from keyboards import main
from auth import get_client, disconnect_client
from forwarder import setup, cleanup
from logger import logger
from pathlib import Path

router = Router()


@router.message(F.text == "▶️ Запустити")
async def start_forwarding(message: Message):
    if not storage.accounts:
        await message.answer("❌ Немає акаунтів")
        return
    
    if not storage.links:
        await message.answer("❌ Немає зв'язків")
        return
    
    user_id = message.from_user.id
    
    if user_id in storage.active_forwarders:
        await message.answer("⚠️ Пересилання вже запущено")
        return
    
    try:
        account_name = list(storage.accounts.keys())[0]
        account = storage.accounts[account_name]
        
        session_path = Path(f"sessions/{account_name}.session")
        if not session_path.exists():
            await message.answer(
                f"❌ Файл сесії не знайдено: sessions/{account_name}.session\n\n"
                "Видаліть акаунт та додайте заново."
            )
            logger.error(f"Сесія не знайдена: {session_path}")
            return
        
        client = await get_client(
            account_name,
            account["api_id"],
            account["api_hash"]
        )
        
        if not await client.is_user_authorized():
            await message.answer(
                f"❌ Акаунт '{account_name}' не авторизований\n\n"
                "Видаліть акаунт та додайте заново."
            )
            await disconnect_client(account_name)
            logger.error(f"Акаунт не авторизований: {account_name}")
            return
        
        me = await client.get_me()
        logger.info(f"Авторизовано як: {me.first_name} (@{me.username}) - {me.phone}")
        
        sources_map = {}
        for link in storage.links:
            source = link["source"]
            target = link["target"]
            
            if source not in sources_map:
                sources_map[source] = []
            sources_map[source].append(target)
        
        for source, targets in sources_map.items():
            await setup(client, source, targets)
        
        storage.active_forwarders[user_id] = {
            "client": client,
            "account": account_name,
            "links": storage.links.copy()
        }
        
        logger.info(f"Запущено пересилання для {account_name}")
        await message.answer(
            f"✅ Пересилання запущено\n\n"
            f"👤 Акаунт: {account_name}\n"
            f"📞 {account['phone']}\n"
            f"🔗 Зв'язків: {len(storage.links)}",
            reply_markup=main()
        )
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Помилка запуску: {e}", exc_info=True)
        await message.answer(f"❌ Помилка: {str(e)}")


@router.message(F.text == "⏸ Зупинити")
async def stop_forwarding(message: Message):
    user_id = message.from_user.id
    
    if user_id not in storage.active_forwarders:
        await message.answer("⚠️ Пересилання не запущено")
        return
    
    try:
        forwarder = storage.active_forwarders[user_id]
        account_name = forwarder["account"]
        
        await disconnect_client(account_name)
        del storage.active_forwarders[user_id]
        cleanup()

        logger.info(f"Зупинено пересилання для {account_name}")
        await message.answer("✅ Пересилання зупинено", reply_markup=main())
    except Exception as e:
        logger.error(f"Помилка зупинки: {e}", exc_info=True)
        await message.answer(f"❌ Помилка: {str(e)}")