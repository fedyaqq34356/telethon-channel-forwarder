import asyncio
from telethon import events
from telethon.tl.types import MessageMediaWebPage
from logger import logger
from storage import storage

target_queues = {}
target_workers = {}


async def _worker(client, target, queue):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break

        msg, footer = item
        try:
            if msg.media and isinstance(msg.media, MessageMediaWebPage):
                new_text = (msg.message or "") + footer
                await client.send_message(
                    target, new_text,
                    formatting_entities=msg.entities,
                    link_preview=True
                )
            elif msg.media:
                new_caption = (msg.message or "") + footer
                await client.send_file(
                    target, msg.media,
                    caption=new_caption,
                    formatting_entities=msg.entities
                )
            else:
                new_text = (msg.message or "") + footer
                await client.send_message(
                    target, new_text,
                    formatting_entities=msg.entities,
                    link_preview=False
                )
            logger.info(f"Переслано → {target.id}")
        except Exception as e:
            logger.error(f"Помилка пересилання до {target.id}: {e}")
        finally:
            queue.task_done()

        interval = storage.interval
        if interval > 0:
            await asyncio.sleep(interval)


def cleanup():
    for task in target_workers.values():
        task.cancel()
    target_queues.clear()
    target_workers.clear()


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

    for target in target_entities:
        tid = target.id
        if tid not in target_queues:
            target_queues[tid] = asyncio.Queue()
            target_workers[tid] = asyncio.create_task(
                _worker(client, target, target_queues[tid])
            )

    logger.info(f"Налаштовано пересилання: {source} → {[str(t.id) for t in target_entities]}")

    @client.on(events.NewMessage(chats=source_entity))
    async def handler(event):
        msg = event.message

        dedup_key = f"{source_entity.id}:{msg.id}"
        if storage.is_duplicate(dedup_key):
            logger.info(f"Дублікат пропущено: {dedup_key}")
            return
        storage.mark_seen(dedup_key)

        msg_text = msg.message or ""
        for keyword in storage.filters:
            if keyword in msg_text.lower():
                logger.info(f"Відфільтровано по '{keyword}': {msg_text[:50]}")
                return

        for target in target_entities:
            await target_queues[target.id].put((msg, ""))
            logger.info(f"В чергу: {source} → {target.id}")
