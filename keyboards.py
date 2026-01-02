from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    buttons = [
        [KeyboardButton(text="➕ Додати акаунт")],
        [KeyboardButton(text="📋 Список акаунтів")],
        [KeyboardButton(text="🗑 Видалити акаунт")],
        [KeyboardButton(text="📺 Додати канал-джерело")],
        [KeyboardButton(text="📤 Додати канал-отримувач")],
        [KeyboardButton(text="🔗 Зв'язати канали")],
        [KeyboardButton(text="📜 Список зв'язків")],
        [KeyboardButton(text="🗑 Видалити зв'язок")],
        [KeyboardButton(text="🗑 Видалити канал")],
        [KeyboardButton(text="▶️ Запустити пересилання")],
        [KeyboardButton(text="⏸ Зупинити пересилання")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def cancel_menu():
    buttons = [[KeyboardButton(text="❌ Скасувати")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def channel_type_menu():
    buttons = [
        [KeyboardButton(text="📺 Канал-джерело")],
        [KeyboardButton(text="📤 Канал-отримувач")],
        [KeyboardButton(text="❌ Скасувати")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)