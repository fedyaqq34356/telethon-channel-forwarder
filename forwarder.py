from telethon import events
from telethon.tl.types import MessageMediaWebPage
from logger import logger


async def setup(client, source, targets):
    await client.get_dialogs()
    
    source_id = int(source) if source.lstrip('-').isdigit() else source
    source_entity = await client.get_entity(source_id)
    
    target_entities = []
    for t in targets:
        t_id = int(t) if t.lstrip('-').isdigit() else t
        target_entities.append(await client.get_entity(t_id))
    
    @client.on(events.NewMessage(chats=source_entity))
    async def handler(event):
        msg = event.message
        
        for target in target_entities:
            try:
                # Проверяем тип медиа
                if msg.media and isinstance(msg.media, MessageMediaWebPage):
                    # Для веб-превью отправляем как обычное сообщение
                    await client.send_message(
                        target,
                        msg.message,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities,
                        link_preview=True
                    )
                elif msg.media:
                    # Для других типов медиа (фото, видео, документы и т.д.)
                    await client.send_file(
                        target,
                        msg.media,
                        caption=msg.message,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities
                    )
                else:
                    # Обычное текстовое сообщение
                    await client.send_message(
                        target,
                        msg.message,
                        parse_mode="html" if msg.entities else None,
                        formatting_entities=msg.entities,
                        link_preview=False
                    )
                logger.info(f"Переслано: {source} → {target}")
            except Exception as e:
                logger.error(f"Помилка пересилання: {e}")