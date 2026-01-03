from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states import Account
from keyboards import main, cancel
from auth import start, verify_code, verify_password, cancel as cancel_auth, disconnect_client
from storage import storage

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Бот для пересилання повідомлень", reply_markup=main())


@router.message(F.text == "❌ Скасувати")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await cancel_auth(message.from_user.id)
    await message.answer("Скасовано", reply_markup=main())


@router.message(F.text == "➕ Додати акаунт")
async def add_account(message: Message, state: FSMContext):
    await state.set_state(Account.session_name)
    await message.answer("Введіть назву сесії:", reply_markup=cancel())


@router.message(Account.session_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if name in storage.accounts:
        await message.answer("Акаунт з такою назвою існує")
        return
    
    await state.update_data(name=name)
    await state.set_state(Account.api_id)
    await message.answer("Введіть API ID:")


@router.message(Account.api_id)
async def process_api_id(message: Message, state: FSMContext):
    try:
        api_id = int(message.text.strip())
        await state.update_data(api_id=api_id)
        await state.set_state(Account.api_hash)
        await message.answer("Введіть API Hash:")
    except ValueError:
        await message.answer("API ID має бути числом")


@router.message(Account.api_hash)
async def process_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text.strip())
    await state.set_state(Account.phone)
    await message.answer("Введіть номер (+380XXXXXXXXX):")


@router.message(Account.phone)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    
    success, result = await start(
        message.from_user.id,
        data["name"],
        data["api_id"],
        data["api_hash"],
        message.text.strip()
    )
    
    if success:
        await state.set_state(Account.code)
        await message.answer(f"{result}\n\nВведіть код через пробіл:\n6 2 3 7 8")
    else:
        await state.clear()
        await message.answer(f"❌ {result}", reply_markup=main())


@router.message(Account.code)
async def process_code(message: Message, state: FSMContext):
    digits = [d.strip() for d in message.text.split() if d.strip().isdigit()]
    
    if len(digits) != 5:
        await message.answer("Код має містити 5 цифр через пробіл")
        return
    
    code = "".join(digits)
    result_type, result_msg = await verify_code(message.from_user.id, code)
    
    if result_type is True:
        await state.clear()
        await message.answer(f"✅ {result_msg}", reply_markup=main())
    elif result_type == "2fa":
        await state.set_state(Account.password)
        await message.answer(result_msg)
    elif result_type == "retry":
        await message.answer(f"❌ {result_msg}")
    else:
        await state.clear()
        await cancel_auth(message.from_user.id)
        await message.answer(f"❌ {result_msg}", reply_markup=main())


@router.message(Account.password)
async def process_password(message: Message, state: FSMContext):
    success, result = await verify_password(message.from_user.id, message.text.strip())
    await state.clear()
    
    if success:
        await message.answer(f"✅ {result}", reply_markup=main())
    else:
        await cancel_auth(message.from_user.id)
        await message.answer(f"❌ {result}", reply_markup=main())


@router.message(F.text == "📋 Список акаунтів")
async def list_accounts(message: Message):
    if not storage.accounts:
        await message.answer("Немає акаунтів")
        return
    
    text = "📱 Акаунти:\n\n"
    for i, (name, acc) in enumerate(storage.accounts.items(), 1):
        text += f"{i}. 🟢 {name}\n   📞 {acc['phone']}\n\n"
    
    await message.answer(text)


@router.message(F.text == "🗑 Видалити акаунт")
async def delete_account(message: Message, state: FSMContext):
    if not storage.accounts:
        await message.answer("Немає акаунтів")
        return
    
    await state.set_state(Account.delete_choice)
    
    text = "Виберіть акаунт (номер):\n\n"
    for i, name in enumerate(storage.accounts.keys(), 1):
        text += f"{i}. {name}\n"
    
    await message.answer(text, reply_markup=cancel())


@router.message(Account.delete_choice, F.text.regexp(r"^\d+$"))
async def process_delete(message: Message, state: FSMContext):
    try:
        idx = int(message.text) - 1
        names = list(storage.accounts.keys())
        
        if 0 <= idx < len(names):
            name = names[idx]
            
            try:
                await disconnect_client(name)
            except:
                pass
            
            storage.remove_account(name)
            await state.clear()
            await message.answer(f"✅ Акаунт '{name}' видалено", reply_markup=main())
        else:
            await message.answer("Невірний номер")
    except ValueError:
        await message.answer("Помилка вводу")