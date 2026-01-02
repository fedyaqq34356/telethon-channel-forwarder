from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import LinkChannels
from keyboards import main_menu, cancel_menu
from storage import storage

router = Router()


@router.message(F.text == "🔗 Зв'язати канали")
async def link_channels_start(message: Message, state: FSMContext):
    if not storage.source_channels:
        await message.answer("❌ Немає каналів-джерел!")
        return
    
    if not storage.target_channels:
        await message.answer("❌ Немає каналів-отримувачів!")
        return
    
    await state.set_state(LinkChannels.choosing_source)
    
    text = "Виберіть канал-джерело (відправте номер):\n\n"
    for i, channel in enumerate(storage.source_channels, 1):
        text += f"{i}. {channel}\n"
    
    await message.answer(text, reply_markup=cancel_menu())


@router.message(LinkChannels.choosing_source, F.text.regexp(r"^\d+$"))
async def process_source_choice(message: Message, state: FSMContext):
    try:
        idx = int(message.text) - 1
        
        if 0 <= idx < len(storage.source_channels):
            source = storage.source_channels[idx]
            await state.update_data(source=source)
            await state.set_state(LinkChannels.choosing_target)
            
            text = f"Джерело: {source}\n\nВиберіть канал-отримувач (відправте номер):\n\n"
            for i, channel in enumerate(storage.target_channels, 1):
                text += f"{i}. {channel}\n"
            
            await message.answer(text, reply_markup=cancel_menu())
        else:
            await message.answer("❌ Невірний номер!")
    except ValueError:
        await message.answer("❌ Помилка вводу!")


@router.message(LinkChannels.choosing_target, F.text.regexp(r"^\d+$"))
async def process_target_choice(message: Message, state: FSMContext):
    try:
        idx = int(message.text) - 1
        
        if 0 <= idx < len(storage.target_channels):
            target = storage.target_channels[idx]
            data = await state.get_data()
            source = data["source"]
            
            link = {"source": source, "target": target}
            
            if link in storage.channel_links:
                await state.clear()
                await message.answer("❌ Цей зв'язок вже існує!", reply_markup=main_menu())
                return
            
            storage.channel_links.append(link)
            storage.save_data()
            
            await state.clear()
            await message.answer(
                f"✅ Зв'язок створено!\n\n"
                f"📺 Джерело: {source}\n"
                f"📤 Отримувач: {target}",
                reply_markup=main_menu()
            )
        else:
            await message.answer("❌ Невірний номер!")
    except ValueError:
        await message.answer("❌ Помилка вводу!")


@router.message(F.text == "📜 Список зв'язків")
async def show_links(message: Message):
    if not storage.channel_links:
        await message.answer("❌ Немає зв'язків між каналами")
        return
    
    text = "📜 <b>Список зв'язків:</b>\n\n"
    
    for i, link in enumerate(storage.channel_links, 1):
        text += f"{i}. 📺 {link['source']}\n   ⬇️\n   📤 {link['target']}\n\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🗑 Видалити зв'язок")
async def delete_link_start(message: Message):
    if not storage.channel_links:
        await message.answer("❌ Немає зв'язків для видалення")
        return
    
    text = "Виберіть зв'язок для видалення (відправте номер):\n\n"
    
    for i, link in enumerate(storage.channel_links, 1):
        text += f"{i}. 📺 {link['source']} → 📤 {link['target']}\n"
    
    await message.answer(text, reply_markup=cancel_menu())


@router.message(F.text.regexp(r"^\d+$"), ~F.state())
async def process_link_deletion(message: Message):
    if not storage.channel_links:
        return
    
    try:
        idx = int(message.text) - 1
        
        if 0 <= idx < len(storage.channel_links):
            link = storage.channel_links.pop(idx)
            storage.save_data()
            await message.answer(
                f"✅ Зв'язок видалено!\n\n"
                f"📺 {link['source']}\n"
                f"📤 {link['target']}",
                reply_markup=main_menu()
            )
    except:
        pass