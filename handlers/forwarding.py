from aiogram import Router, F
from aiogram.types import Message
from telethon import events
from storage import storage
from keyboards import main_menu
from telethon_auth import get_account_client

router = Router()


async def setup_forwarder(client, source, targets):
    await client.get_dialogs()
    
    if isinstance(source, str) and source.lstrip('-').isdigit():
        source = int(source)
    
    source_entity = await client.get_entity(source)
    
    target_entities = []
    for t in targets:
        if isinstance(t, str) and t.lstrip('-').isdigit():
            t = int(t)
        target_entities.append(await client.get_entity(t))
    
    @client.on(events.NewMessage(chats=source_entity))
    async def handler(event):
        msg = event.message
        for target_entity in target_entities:
            try:
                if msg.media:
                    await client.send_file(
                        target_entity,
                        msg.media,
                        caption=msg.message,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities
                    )
                else:
                    await client.send_message(
                        target_entity,
                        msg.message,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities,
                        link_preview=False
                    )
            except Exception as e:
                print(f"Помилка пересилання: {e}")


@router.message(F.text == "▶️ Запустити пересилання")
async def start_forwarding(message: Message):
    if not storage.accounts:
        await message.answer("❌ Немає доданих акаунтів!")
        return
    
    if not storage.channel_links:
        await message.answer("❌ Немає зв'язків між каналами!")
        return
    
    user_id = message.from_user.id
    
    if user_id in storage.active_forwarders:
        await message.answer("⚠️ Пересилання вже запущено!")
        return
    
    try:
        account_name = list(storage.accounts.keys())[0]
        account = storage.accounts[account_name]
        
        client = await get_account_client(
            account_name,
            account["api_id"],
            account["api_hash"]
        )
        
        if not client.is_connected():
            await client.connect()
        
        if not await client.is_user_authorized():
            await message.answer("❌ Акаунт не авторизований! Видаліть і додайте акаунт заново.")
            await client.disconnect()
            return
        
        sources_map = {}
        for link in storage.channel_links:
            source = link["source"]
            target = link["target"]
            
            if source not in sources_map:
                sources_map[source] = []
            sources_map[source].append(target)
        
        for source, targets in sources_map.items():
            await setup_forwarder(client, source, targets)
        
        storage.active_forwarders[user_id] = {
            "client": client,
            "account_name": account_name,
            "links": storage.channel_links.copy()
        }
        
        await message.answer(
            "✅ Пересилання запущено!\n\n"
            f"🔗 Зв'язків: {len(storage.channel_links)}",
            reply_markup=main_menu()
        )
    except Exception as e:
        await message.answer(f"❌ Помилка запуску: {str(e)}")


@router.message(F.text == "⏸ Зупинити пересилання")
async def stop_forwarding(message: Message):
    user_id = message.from_user.id
    
    if user_id not in storage.active_forwarders:
        await message.answer("⚠️ Пересилання не запущено!")
        return
    
    try:
        forwarder = storage.active_forwarders[user_id]
        client = forwarder["client"]
        
        client.remove_event_handler(None)
        
        if client.is_connected():
            await client.disconnect()
        
        del storage.active_forwarders[user_id]
        
        await message.answer("✅ Пересилання зупинено!", reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Помилка зупинки: {str(e)}")