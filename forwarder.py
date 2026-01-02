from telethon import events

async def setup_forwarder(client, source, target):
    await client.get_dialogs()
    
    source_entity = await client.get_entity(source)
    target_entity = await client.get_entity(target)
    
    @client.on(events.NewMessage(chats=source_entity))
    async def handler(event):
        msg = event.message
        
        if msg.media:
            await client.send_file(
                target_entity,
                msg.media,
                caption=msg.message,
                parse_mode='html' if msg.entities else None,
                formatting_entities=msg.entities
            )
        else:
            await client.send_message(
                target_entity,
                msg.message,
                parse_mode='html' if msg.entities else None,
                formatting_entities=msg.entities,
                link_preview=False
            )