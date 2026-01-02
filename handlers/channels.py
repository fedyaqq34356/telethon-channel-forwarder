from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import AddSourceChannel, AddTargetChannel, DeleteChannel
from keyboards import main_menu, cancel_menu, channel_type_menu
from storage import storage


router = Router()


@router.message(F.text == "📺 Додати канал-джерело")
async def add_source_channel(message: Message, state: FSMContext):
    await state.set_state(AddSourceChannel.waiting_username)
    await message.answer(
        "Введіть username або ID каналу-джерела:\n"
        "(Наприклад: @channel або -1001234567890)",
        reply_markup=cancel_menu()
    )


@router.message(AddSourceChannel.waiting_username)
async def process_source_channel(message: Message, state: FSMContext):
    channel = message.text.strip()
    
    if channel in storage.source_channels:
        await message.answer("❌ Цей канал вже додано!")
        return
    
    storage.source_channels.append(channel)
    storage.save_data()
    
    await state.clear()
    await message.answer(f"✅ Канал-джерело {channel} додано!", reply_markup=main_menu())


@router.message(F.text == "📤 Додати канал-отримувач")
async def add_target_channel(message: Message, state: FSMContext):
    await state.set_state(AddTargetChannel.waiting_username)
    await message.answer(
        "Введіть username або ID каналу-отримувача:\n"
        "(Наприклад: @channel або -1001234567890)",
        reply_markup=cancel_menu()
    )


@router.message(AddTargetChannel.waiting_username)
async def process_target_channel(message: Message, state: FSMContext):
    channel = message.text.strip()
    
    if channel in storage.target_channels:
        await message.answer("❌ Цей канал вже додано!")
        return
    
    storage.target_channels.append(channel)
    storage.save_data()
    
    await state.clear()
    await message.answer(f"✅ Канал-отримувач {channel} додано!", reply_markup=main_menu())


@router.message(F.text == "🗑 Видалити канал")
async def delete_channel_start(message: Message, state: FSMContext):
    if not storage.source_channels and not storage.target_channels:
        await message.answer("❌ Немає доданих каналів")
        return
    
    await state.set_state(DeleteChannel.choosing_type)
    await message.answer(
        "Оберіть тип каналу для видалення:",
        reply_markup=channel_type_menu()
    )


@router.message(DeleteChannel.choosing_type, F.text == "📺 Канал-джерело")
async def choose_source_to_delete(message: Message, state: FSMContext):
    if not storage.source_channels:
        await state.clear()
        await message.answer("❌ Немає каналів-джерел", reply_markup=main_menu())
        return
    
    await state.update_data(channel_type="source")
    await state.set_state(DeleteChannel.choosing_channel)
    
    text = "Виберіть канал-джерело для видалення (відправте номер):\n\n"
    for i, channel in enumerate(storage.source_channels, 1):
        text += f"{i}. {channel}\n"
    
    await message.answer(text, reply_markup=cancel_menu())


@router.message(DeleteChannel.choosing_type, F.text == "📤 Канал-отримувач")
async def choose_target_to_delete(message: Message, state: FSMContext):
    if not storage.target_channels:
        await state.clear()
        await message.answer("❌ Немає каналів-отримувачів", reply_markup=main_menu())
        return
    
    await state.update_data(channel_type="target")
    await state.set_state(DeleteChannel.choosing_channel)
    
    text = "Виберіть канал-отримувач для видалення (відправте номер):\n\n"
    for i, channel in enumerate(storage.target_channels, 1):
        text += f"{i}. {channel}\n"
    
    await message.answer(text, reply_markup=cancel_menu())


@router.message(DeleteChannel.choosing_channel, F.text.regexp(r"^\d+$"))
async def process_channel_deletion(message: Message, state: FSMContext):
    data = await state.get_data()
    channel_type = data.get("channel_type")
    
    try:
        idx = int(message.text) - 1
        
        if channel_type == "source":
            if 0 <= idx < len(storage.source_channels):
                channel = storage.source_channels.pop(idx)
                
                storage.channel_links = [
                    link for link in storage.channel_links 
                    if link["source"] != channel
                ]
                
                storage.save_data()
                await state.clear()
                await message.answer(f"✅ Канал-джерело {channel} видалено!", reply_markup=main_menu())
            else:
                await message.answer("❌ Невірний номер!")
        elif channel_type == "target":
            if 0 <= idx < len(storage.target_channels):
                channel = storage.target_channels.pop(idx)
                
                storage.channel_links = [
                    link for link in storage.channel_links 
                    if link["target"] != channel
                ]
                
                storage.save_data()
                await state.clear()
                await message.answer(f"✅ Канал-отримувач {channel} видалено!", reply_markup=main_menu())
            else:
                await message.answer("❌ Невірний номер!")
    except ValueError:
        await message.answer("❌ Помилка вводу!")