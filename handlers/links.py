from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import Link
from keyboards import main, cancel
from storage import storage

router = Router()


@router.message(F.text == "🔗 Зв'язати канали")
async def link_start(message: Message, state: FSMContext):
    if not storage.source_channels:
        await message.answer("Немає джерел")
        return
    
    if not storage.target_channels:
        await message.answer("Немає отримувачів")
        return
    
    await state.set_state(Link.source)
    
    text = "Виберіть джерело (номер):\n\n"
    for i, ch in enumerate(storage.source_channels, 1):
        text += f"{i}. {ch}\n"
    
    await message.answer(text, reply_markup=cancel())


@router.message(Link.source, F.text.regexp(r"^\d+$"))
async def process_source(message: Message, state: FSMContext):
    try:
        idx = int(message.text) - 1
        
        if 0 <= idx < len(storage.source_channels):
            source = storage.source_channels[idx]
            await state.update_data(source=source)
            await state.set_state(Link.target)
            
            text = f"Джерело: {source}\n\nВиберіть отримувач (номер):\n\n"
            for i, ch in enumerate(storage.target_channels, 1):
                text += f"{i}. {ch}\n"
            
            await message.answer(text, reply_markup=cancel())
        else:
            await message.answer("Невірний номер")
    except ValueError:
        await message.answer("Помилка вводу")


@router.message(Link.target, F.text.regexp(r"^\d+$"))
async def process_target(message: Message, state: FSMContext):
    try:
        idx = int(message.text) - 1
        
        if 0 <= idx < len(storage.target_channels):
            target = storage.target_channels[idx]
            data = await state.get_data()
            source = data["source"]
            
            link = {"source": source, "target": target}
            
            if link in storage.links:
                await state.clear()
                await message.answer("Зв'язок існує", reply_markup=main())
                return
            
            storage.add_link(source, target)
            await state.clear()
            await message.answer(
                f"✅ Зв'язок створено\n\n📺 {source}\n📤 {target}",
                reply_markup=main()
            )
        else:
            await message.answer("Невірний номер")
    except ValueError:
        await message.answer("Помилка вводу")


@router.message(F.text == "📜 Список зв'язків")
async def list_links(message: Message):
    if not storage.links:
        await message.answer("Немає зв'язків")
        return
    
    text = "📜 <b>Зв'язки:</b>\n\n"
    for i, link in enumerate(storage.links, 1):
        text += f"{i}. 📺 {link['source']}\n   ⬇️\n   📤 {link['target']}\n\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🗑 Видалити зв'язок")
async def delete_link(message: Message, state: FSMContext):
    if not storage.links:
        await message.answer("Немає зв'язків")
        return
    
    await state.set_state(Link.delete_choice)
    
    text = "Виберіть зв'язок (номер):\n\n"
    for i, link in enumerate(storage.links, 1):
        text += f"{i}. 📺 {link['source']} → 📤 {link['target']}\n"
    
    await message.answer(text, reply_markup=cancel())


@router.message(Link.delete_choice, F.text.regexp(r"^\d+$"))
async def process_link_delete(message: Message, state: FSMContext):
    try:
        idx = int(message.text) - 1
        
        if 0 <= idx < len(storage.links):
            link = storage.links[idx]
            storage.remove_link(idx)
            await state.clear()
            await message.answer(
                f"✅ Зв'язок видалено\n\n📺 {link['source']}\n📤 {link['target']}",
                reply_markup=main()
            )
        else:
            await message.answer("Невірний номер")
    except ValueError:
        await message.answer("Помилка вводу")