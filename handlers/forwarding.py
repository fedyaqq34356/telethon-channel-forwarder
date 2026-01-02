from aiogram import Router, F
from aiogram.types import Message
from storage import storage
from keyboards import main
from auth import get_client
from forwarder import setup
from logger import logger

router = Router()


@router.message(F.text == "▶️ Запустити")
async def start_forwarding(message: Message):
    if not storage.accounts:
        await message.answer("Немає акаунтів")
        return
    
    if not storage.links:
        await message.answer("Немає зв'язків")
        return
    
    user_id = message.from_user.id
    
    if user_id in storage.active_forwarders:
        await message.answer("Пересилання вже запущено")
        return
    
    try:
        account_name = list(storage.accounts.keys())[0]
        account = storage.accounts[account_name]
        
        client = await get_client(
            account_name,
            account["api_id"],
            account["api_hash"]
        )
        
        if not client.is_connected():
            await client.connect()
        
        if not await client.is_user_authorized():
            await message.answer("Акаунт не авторизований")
            await client.disconnect()
            return
        
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
            f"✅ Пересилання запущено\n\n🔗 Зв'язків: {len(storage.links)}",
            reply_markup=main()
        )
    except Exception as e:
        logger.error(f"Помилка запуску: {e}")
        await message.answer(f"❌ Помилка: {str(e)}")


@router.message(F.text == "⏸ Зупинити")
async def stop_forwarding(message: Message):
    user_id = message.from_user.id
    
    if user_id not in storage.active_forwarders:
        await message.answer("Пересилання не запущено")
        return
    
    try:
        forwarder = storage.active_forwarders[user_id]
        client = forwarder["client"]
        
        client.remove_event_handler(None)
        
        if client.is_connected():
            await client.disconnect()
        
        del storage.active_forwarders[user_id]
        
        logger.info(f"Зупинено пересилання для {forwarder['account']}")
        await message.answer("✅ Пересилання зупинено", reply_markup=main())
    except Exception as e:
        logger.error(f"Помилка зупинки: {e}")
        await message.answer(f"❌ Помилка: {str(e)}")