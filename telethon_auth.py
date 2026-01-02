from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from pathlib import Path


auth_sessions = {}


async def start_auth(user_id, session_name, api_id, api_hash, phone):
    try:
        Path("sessions").mkdir(exist_ok=True)
        
        client = TelegramClient(f"sessions/{session_name}", api_id, api_hash)
        await client.connect()
        
        if await client.is_user_authorized():
            await client.disconnect()
            return False, "❌ Цей акаунт вже авторизований!"
        
        await client.send_code_request(phone)
        
        auth_sessions[user_id] = {
            "client": client,
            "phone": phone,
            "session_name": session_name,
            "api_id": api_id,
            "api_hash": api_hash
        }
        
        return True, "✅ Код надіслано на ваш номер!"
    except Exception as e:
        return False, f"Помилка: {str(e)}"


async def submit_code(user_id, code):
    if user_id not in auth_sessions:
        return False, "❌ Сесія авторизації не знайдена!"
    
    session = auth_sessions[user_id]
    client = session["client"]
    phone = session["phone"]
    
    try:
        await client.sign_in(phone, code)
        
        from storage import storage
        storage.accounts[session["session_name"]] = {
            "api_id": session["api_id"],
            "api_hash": session["api_hash"],
            "phone": phone
        }
        storage.save_data()
        
        await client.disconnect()
        del auth_sessions[user_id]
        return True, "✅ Акаунт успішно додано!"
        
    except SessionPasswordNeededError:
        return "2fa", "🔐 Введіть пароль двофакторної автентифікації:"
    except PhoneCodeInvalidError:
        return "retry", "❌ Невірний код! Спробуйте ще раз:"
    except Exception as e:
        return False, f"Помилка: {str(e)}"


async def submit_password(user_id, password):
    if user_id not in auth_sessions:
        return False, "❌ Сесія авторизації не знайдена!"
    
    session = auth_sessions[user_id]
    client = session["client"]
    
    try:
        await client.sign_in(password=password)
        
        from storage import storage
        storage.accounts[session["session_name"]] = {
            "api_id": session["api_id"],
            "api_hash": session["api_hash"],
            "phone": session["phone"]
        }
        storage.save_data()
        
        await client.disconnect()
        del auth_sessions[user_id]
        return True, "✅ Акаунт успішно додано!"
    except Exception as e:
        return False, f"Помилка: {str(e)}"


async def cancel_auth(user_id):
    if user_id in auth_sessions:
        client = auth_sessions[user_id]["client"]
        if client.is_connected():
            await client.disconnect()
        del auth_sessions[user_id]


async def get_account_client(session_name, api_id, api_hash):
    Path("sessions").mkdir(exist_ok=True)
    client = TelegramClient(f"sessions/{session_name}", api_id, api_hash)
    await client.connect()
    return client