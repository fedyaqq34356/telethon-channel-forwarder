from telethon import events
from telethon.tl.types import MessageMediaWebPage
from logger import logger


message_cache = {}


async def setup(client, source, targets):
    await client.get_dialogs()
    
    try:
        if source.startswith('@'):
            source_entity = await client.get_entity(source)
        elif source.lstrip('-').isdigit():
            source_id = int(source)
            try:
                source_entity = await client.get_entity(source_id)
            except ValueError:
                logger.warning(f"Канал {source} не знайдено в кеші, спроба отримати...")
                from telethon.tl.types import InputPeerChannel
                if source_id < 0:
                    channel_id = int(str(abs(source_id))[3:])
                else:
                    channel_id = source_id
                
                dialogs = await client.get_dialogs()
                for dialog in dialogs:
                    if hasattr(dialog.entity, 'id') and dialog.entity.id == channel_id:
                        source_entity = dialog.entity
                        break
                else:
                    raise ValueError(f"Не вдалося знайти канал {source}. Переконайтеся, що акаунт є учасником цього каналу.")
        else:
            source_entity = await client.get_entity(source)
    except Exception as e:
        logger.error(f"Помилка отримання джерела {source}: {e}")
        raise ValueError(f"Не вдалося отримати джерело {source}. Переконайтеся, що:\n1. Акаунт є учасником каналу\n2. ID або username вказано правильно")
    
    target_entities = []
    for t in targets:
        try:
            if t.startswith('@'):
                target_entities.append(await client.get_entity(t))
            elif t.lstrip('-').isdigit():
                t_id = int(t)
                try:
                    target_entities.append(await client.get_entity(t_id))
                except ValueError:
                    logger.warning(f"Канал {t} не знайдено в кеші, спроба отримати...")
                    if t_id < 0:
                        channel_id = int(str(abs(t_id))[3:])
                    else:
                        channel_id = t_id
                    
                    dialogs = await client.get_dialogs()
                    for dialog in dialogs:
                        if hasattr(dialog.entity, 'id') and dialog.entity.id == channel_id:
                            target_entities.append(dialog.entity)
                            break
                    else:
                        raise ValueError(f"Не вдалося знайти канал {t}. Переконайтеся, що акаунт має права на відправку в цей канал.")
            else:
                target_entities.append(await client.get_entity(t))
        except Exception as e:
            logger.error(f"Помилка отримання отримувача {t}: {e}")
            raise ValueError(f"Не вдалося отримати отримувач {t}. Переконайтеся, що:\n1. Акаунт має права на відправку\n2. ID або username вказано правильно")
    
    logger.info(f"Налаштовано пересилання: {source} → {[str(t.id) for t in target_entities]}")
    
    @client.on(events.NewMessage(chats=source_entity))
    async def handler(event):
        msg = event.message
        
        if msg.message and '@relax_adminz' in msg.message.lower():
            logger.info(f"Пропущено повідомлення з @relax_adminz від {source}")
            return
        
        msg_text = msg.message or ""
        cache_key = f"{source}:{msg_text[:100]}"
        
        if cache_key in message_cache:
            logger.info(f"Пропущено дублікат: {cache_key}")
            return
        
        message_cache[cache_key] = True
        
        source_name = getattr(source_entity, 'username', None)
        if source_name:
            source_label = f"@{source_name}"
        else:
            source_label = getattr(source_entity, 'title', source)
        
        footer = f"\n\n📺 Джерело: {source_label}"
        
        for target in target_entities:
            try:
                if msg.media and isinstance(msg.media, MessageMediaWebPage):
                    new_text = (msg.message or "") + footer
                    await client.send_message(
                        target,
                        new_text,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities,
                        link_preview=True
                    )
                elif msg.media:
                    new_caption = (msg.message or "") + footer
                    await client.send_file(
                        target,
                        msg.media,
                        caption=new_caption,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities
                    )
                else:
                    new_text = (msg.message or "") + footer
                    await client.send_message(
                        target,
                        new_text,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities,
                        link_preview=False
                    )
                logger.info(f"Переслано: {source} → {target.id}")
            except Exception as e:
                logger.error(f"Помилка пересилання до {target.id}: {e}")
        
        if len(message_cache) > 1000:
            message_cache.clear()