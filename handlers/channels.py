from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import Channel
from keyboards import main, cancel, channel_type
from storage import storage

router = Router()


@router.message(F.text == "📺 Додати джерело")
async def add_source(message: Message, state: FSMContext):
    await state.set_state(Channel.source)
    await message.answer(
        "Введіть username або ID:\n(@channel або -1001234567890)",
        reply_markup=cancel()
    )


@router.message(Channel.source)
async def process_source(message: Message, state: FSMContext):
    channel = message.text.strip()
    
    if channel in storage.source_channels:
        await message.answer("Канал вже додано")
        return
    
    storage.add_source(channel)
    await state.clear()
    await message.answer(f"✅ Джерело {channel} додано", reply_markup=main())


@router.message(F.text == "📤 Додати отримувач")
async def add_target(message: Message, state: FSMContext):
    await state.set_state(Channel.target)
    await message.answer(
        "Введіть username або ID:\n(@channel або -1001234567890)",
        reply_markup=cancel()
    )


@router.message(Channel.target)
async def process_target(message: Message, state: FSMContext):
    channel = message.text.strip()
    
    if channel in storage.target_channels:
        await message.answer("Канал вже додано")
        return
    
    storage.add_target(channel)
    await state.clear()
    await message.answer(f"✅ Отримувач {channel} додано", reply_markup=main())


@router.message(F.text == "📋 Всі канали")
async def list_all_channels(message: Message):
    if not storage.source_channels and not storage.target_channels:
        await message.answer("Немає каналів")
        return
    
    text = "📋 <b>Всі канали:</b>\n\n"
    
    if storage.source_channels:
        text += "📺 <b>Джерела:</b>\n"
        for i, ch in enumerate(storage.source_channels, 1):
            text += f"{i}. {ch}\n"
        text += "\n"
    
    if storage.target_channels:
        text += "📤 <b>Отримувачі:</b>\n"
        for i, ch in enumerate(storage.target_channels, 1):
            text += f"{i}. {ch}\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🗑 Видалити канал")
async def delete_channel(message: Message, state: FSMContext):
    if not storage.source_channels and not storage.target_channels:
        await message.answer("Немає каналів")
        return
    
    await state.set_state(Channel.delete_type)
    await message.answer("Оберіть тип каналу:", reply_markup=channel_type())


@router.message(Channel.delete_type, F.text == "📺 Джерело")
async def delete_source_choice(message: Message, state: FSMContext):
    if not storage.source_channels:
        await state.clear()
        await message.answer("Немає джерел", reply_markup=main())
        return
    
    await state.update_data(type="source")
    await state.set_state(Channel.delete_choice)
    
    text = "Виберіть джерело (номер):\n\n"
    for i, ch in enumerate(storage.source_channels, 1):
        text += f"{i}. {ch}\n"
    
    await message.answer(text, reply_markup=cancel())


@router.message(Channel.delete_type, F.text == "📤 Отримувач")
async def delete_target_choice(message: Message, state: FSMContext):
    if not storage.target_channels:
        await state.clear()
        await message.answer("Немає отримувачів", reply_markup=main())
        return
    
    await state.update_data(type="target")
    await state.set_state(Channel.delete_choice)
    
    text = "Виберіть отримувач (номер):\n\n"
    for i, ch in enumerate(storage.target_channels, 1):
        text += f"{i}. {ch}\n"
    
    await message.answer(text, reply_markup=cancel())


@router.message(Channel.delete_choice, F.text.regexp(r"^\d+$"))
async def process_channel_delete(message: Message, state: FSMContext):
    data = await state.get_data()
    channel_type = data.get("type")
    
    try:
        idx = int(message.text) - 1
        
        if channel_type == "source":
            if 0 <= idx < len(storage.source_channels):
                channel = storage.source_channels[idx]
                storage.remove_source(channel)
                await state.clear()
                await message.answer(f"✅ Джерело {channel} видалено", reply_markup=main())
            else:
                await message.answer("Невірний номер")
        elif channel_type == "target":
            if 0 <= idx < len(storage.target_channels):
                channel = storage.target_channels[idx]
                storage.remove_target(channel)
                await state.clear()
                await message.answer(f"✅ Отримувач {channel} видалено", reply_markup=main())
            else:
                await message.answer("Невірний номер")
    except ValueError:
        await message.answer("Помилка вводу")