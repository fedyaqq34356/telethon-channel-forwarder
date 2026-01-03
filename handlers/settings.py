from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import Settings
from keyboards import main, cancel, settings_kb
from storage import storage

router = Router()


@router.message(F.text == "⚙️ Налаштування")
async def settings_menu(message: Message):
    filters_text = "\n".join(f"{i+1}. {f}" for i, f in enumerate(storage.filters)) or "немає"
    text = (
        "⚙️ <b>Налаштування</b>\n\n"
        f"⏱ Інтервал між постами: <b>{storage.interval} сек</b>\n\n"
        f"🔎 Фільтри (стоп-слова):\n{filters_text}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=settings_kb())


@router.message(F.text == "◀️ Назад")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Головне меню", reply_markup=main())


@router.message(F.text == "⏱ Встановити інтервал")
async def set_interval_start(message: Message, state: FSMContext):
    await state.set_state(Settings.interval)
    await message.answer(
        f"Поточний інтервал: <b>{storage.interval} сек</b>\n\nВведіть нове значення в секундах (0 = без затримки):",
        parse_mode="HTML",
        reply_markup=cancel()
    )


@router.message(Settings.interval, F.text.regexp(r"^\d+$"))
async def set_interval_done(message: Message, state: FSMContext):
    seconds = int(message.text)
    storage.set_interval(seconds)
    await state.clear()
    await message.answer(f"✅ Інтервал встановлено: {seconds} сек", reply_markup=main())


@router.message(Settings.interval)
async def set_interval_invalid(message: Message):
    await message.answer("Введіть ціле число (секунди)")


@router.message(F.text == "🔎 Додати фільтр")
async def add_filter_start(message: Message, state: FSMContext):
    await state.set_state(Settings.add_filter)
    await message.answer(
        "Введіть стоп-слово (повідомлення з цим словом не будуть пересилатись):",
        reply_markup=cancel()
    )


@router.message(Settings.add_filter)
async def add_filter_done(message: Message, state: FSMContext):
    keyword = message.text.strip().lower()
    if keyword in storage.filters:
        await state.clear()
        await message.answer("Цей фільтр вже існує", reply_markup=main())
        return
    storage.add_filter(keyword)
    await state.clear()
    await message.answer(f"✅ Фільтр '{keyword}' додано", reply_markup=main())


@router.message(F.text == "🗑 Видалити фільтр")
async def remove_filter_start(message: Message, state: FSMContext):
    if not storage.filters:
        await message.answer("Немає фільтрів")
        return

    await state.set_state(Settings.remove_filter)
    text = "Виберіть фільтр для видалення (номер):\n\n"
    for i, f in enumerate(storage.filters, 1):
        text += f"{i}. {f}\n"
    await message.answer(text, reply_markup=cancel())


@router.message(Settings.remove_filter, F.text.regexp(r"^\d+$"))
async def remove_filter_done(message: Message, state: FSMContext):
    idx = int(message.text) - 1
    keyword = storage.remove_filter(idx)
    if keyword is not None:
        await state.clear()
        await message.answer(f"✅ Фільтр '{keyword}' видалено", reply_markup=main())
    else:
        await message.answer("Невірний номер")


@router.message(Settings.remove_filter)
async def remove_filter_invalid(message: Message):
    await message.answer("Введіть номер фільтру")
