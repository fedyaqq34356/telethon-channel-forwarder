from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from pathlib import Path
from logger import logger

sessions = {}


async def start(user_id, name, api_id, api_hash, phone):
    try:
        Path("sessions").mkdir(exist_ok=True)
        
        client = TelegramClient(f"sessions/{name}", api_id, api_hash)
        await client.connect()
        
        if await client.is_user_authorized():
            await client.disconnect()
            return False, "Акаунт вже авторизований"
        
        await client.send_code_request(phone)
        
        sessions[user_id] = {
            "client": client,
            "phone": phone,
            "name": name,
            "api_id": api_id,
            "api_hash": api_hash
        }
        
        logger.info(f"Запит коду для {phone}")
        return True, "Код надіслано"
    except Exception as e:
        logger.error(f"Помилка авторизації: {e}")
        return False, str(e)


async def verify_code(user_id, code):
    if user_id not in sessions:
        return False, "Сесія не знайдена"
    
    session = sessions[user_id]
    
    try:
        await session["client"].sign_in(session["phone"], code)
        
        from storage import storage
        storage.add_account(
            session["name"],
            session["api_id"],
            session["api_hash"],
            session["phone"]
        )
        
        await session["client"].disconnect()
        del sessions[user_id]
        
        logger.info(f"Авторизовано: {session['name']}")
        return True, "Акаунт додано"
        
    except SessionPasswordNeededError:
        return "2fa", "Введіть пароль 2FA"
    except PhoneCodeInvalidError:
        return "retry", "Невірний код"
    except Exception as e:
        logger.error(f"Помилка коду: {e}")
        return False, str(e)


async def verify_password(user_id, password):
    if user_id not in sessions:
        return False, "Сесія не знайдена"
    
    session = sessions[user_id]
    
    try:
        await session["client"].sign_in(password=password)
        
        from storage import storage
        storage.add_account(
            session["name"],
            session["api_id"],
            session["api_hash"],
            session["phone"]
        )
        
        await session["client"].disconnect()
        del sessions[user_id]
        
        logger.info(f"Авторизовано з 2FA: {session['name']}")
        return True, "Акаунт додано"
    except Exception as e:
        logger.error(f"Помилка паролю: {e}")
        return False, str(e)


async def cancel(user_id):
    if user_id in sessions:
        if sessions[user_id]["client"].is_connected():
            await sessions[user_id]["client"].disconnect()
        del sessions[user_id]
        logger.info(f"Скасовано авторизацію: {user_id}")


async def get_client(name, api_id, api_hash):
    Path("sessions").mkdir(exist_ok=True)
    client = TelegramClient(f"sessions/{name}", api_id, api_hash)
    await client.connect()
    return client