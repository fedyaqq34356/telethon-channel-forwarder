from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states import AddAccount
from keyboards import main_menu, cancel_menu
from telethon_auth import start_auth, submit_code, submit_password, cancel_auth, get_account_client
from storage import storage
from pathlib import Path


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    Path("sessions").mkdir(exist_ok=True)
    await message.answer(
        "👋 Вітаю! Я бот для пересилання повідомлень між Telegram каналами.\n\n"
        "Виберіть дію:",
        reply_markup=main_menu()
    )


@router.message(F.text == "❌ Скасувати")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await cancel_auth(message.from_user.id)
    await message.answer("❌ Дію скасовано", reply_markup=main_menu())


@router.message(F.text == "➕ Додати акаунт")
async def add_account_start(message: Message, state: FSMContext):
    await state.set_state(AddAccount.waiting_session_name)
    await message.answer(
        "Введіть унікальну назву для сесії акаунта:\n"
        "(Наприклад: my_account)",
        reply_markup=cancel_menu()
    )


@router.message(AddAccount.waiting_session_name)
async def process_session_name(message: Message, state: FSMContext):
    session_name = message.text.strip()
    
    if session_name in storage.accounts:
        await message.answer("❌ Акаунт з такою назвою вже існує! Введіть іншу назву:")
        return
    
    await state.update_data(session_name=session_name)
    await state.set_state(AddAccount.waiting_api_id)
    await message.answer("Введіть API ID:\n(Отримати можна на https://my.telegram.org)")


@router.message(AddAccount.waiting_api_id)
async def process_api_id(message: Message, state: FSMContext):
    try:
        api_id = int(message.text.strip())
        await state.update_data(api_id=api_id)
        await state.set_state(AddAccount.waiting_api_hash)
        await message.answer("Введіть API Hash:")
    except ValueError:
        await message.answer("❌ API ID має бути числом! Спробуйте ще раз:")


@router.message(AddAccount.waiting_api_hash)
async def process_api_hash(message: Message, state: FSMContext):
    api_hash = message.text.strip()
    await state.update_data(api_hash=api_hash)
    await state.set_state(AddAccount.waiting_phone)
    await message.answer("Введіть номер телефону (у форматі +380XXXXXXXXX):")


@router.message(AddAccount.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    data = await state.get_data()
    
    success, result = await start_auth(
        message.from_user.id,
        data["session_name"],
        data["api_id"],
        data["api_hash"],
        phone
    )
    
    if success:
        await state.set_state(AddAccount.waiting_code)
        await message.answer(
            f"{result}\n\n"
            "💡 <b>Для безпеки введіть код по одній цифрі через пробіл</b>\n"
            "Приклад: 6 2 3 7 8",
            parse_mode="HTML"
        )
    else:
        await state.clear()
        await message.answer(f"❌ {result}", reply_markup=main_menu())


@router.message(AddAccount.waiting_code)
async def process_code(message: Message, state: FSMContext):
    digits = [d.strip() for d in message.text.split() if d.strip().isdigit()]
    
    if len(digits) != 5:
        await message.answer(
            "❌ Код має складатися рівно з 5 цифр, введених через пробіл!\n"
            "Приклад: 6 2 3 7 8\n\nСпробуйте ще раз:"
        )
        return
    
    code = "".join(digits)
    result_type, result_msg = await submit_code(message.from_user.id, code)
    
    if result_type is True:
        await state.clear()
        await message.answer(result_msg, reply_markup=main_menu())
    elif result_type == "2fa":
        await state.set_state(AddAccount.waiting_password)
        await message.answer(result_msg)
    elif result_type == "retry":
        await message.answer(f"{result_msg}\n\n💡 Введіть новий код по одній цифрі через пробіл:")
    else:
        await state.clear()
        await cancel_auth(message.from_user.id)
        await message.answer(f"❌ {result_msg}", reply_markup=main_menu())


@router.message(AddAccount.waiting_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    success, result = await submit_password(message.from_user.id, password)
    
    await state.clear()
    
    if success:
        await message.answer(result, reply_markup=main_menu())
    else:
        await cancel_auth(message.from_user.id)
        await message.answer(f"❌ {result}", reply_markup=main_menu())


@router.message(F.text == "📋 Список акаунтів")
async def show_accounts(message: Message):
    if not storage.accounts:
        await message.answer("❌ Немає доданих акаунтів")
        return
    
    text = "📱 <b>Список акаунтів:</b>\n\n"
    
    for i, (name, acc) in enumerate(storage.accounts.items(), 1):
        status = "🟢"
        phone = acc.get("phone", "немає номера")
        text += f"{i}. {status} <b>{name}</b>\n   📞 {phone}\n\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🗑 Видалити акаунт")
async def delete_account_start(message: Message):
    if not storage.accounts:
        await message.answer("❌ Немає акаунтів для видалення")
        return
    
    text = "Виберіть акаунт для видалення (відправте номер):\n\n"
    
    for i, name in enumerate(storage.accounts.keys(), 1):
        text += f"{i}. {name}\n"
    
    await message.answer(text, reply_markup=cancel_menu())


@router.message(F.text.regexp(r"^\d+$"), ~F.state())
async def process_account_deletion(message: Message):
    try:
        idx = int(message.text) - 1
        acc_list = list(storage.accounts.keys())
        
        if 0 <= idx < len(acc_list):
            name = acc_list[idx]
            
            try:
                acc = storage.accounts[name]
                client = await get_account_client(name, acc["api_id"], acc["api_hash"])
                await client.disconnect()
            except:
                pass
            
            del storage.accounts[name]
            storage.save_data()
            
            await message.answer(f"✅ Акаунт '{name}' видалено!", reply_markup=main_menu())
        else:
            await message.answer("❌ Невірний номер!")
    except:
        await message.answer("❌ Помилка вводу!")