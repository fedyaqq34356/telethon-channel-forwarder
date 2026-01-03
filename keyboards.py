from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Додати акаунт")],
            [KeyboardButton(text="📋 Список акаунтів")],
            [KeyboardButton(text="🗑 Видалити акаунт")],
            [KeyboardButton(text="📺 Додати джерело")],
            [KeyboardButton(text="📤 Додати отримувач")],
            [KeyboardButton(text="📋 Всі канали")],
            [KeyboardButton(text="🗑 Видалити канал")],
            [KeyboardButton(text="🔗 Зв'язати канали")],
            [KeyboardButton(text="📜 Список зв'язків")],
            [KeyboardButton(text="🗑 Видалити зв'язок")],
            [KeyboardButton(text="⚙️ Налаштування")],
            [KeyboardButton(text="▶️ Запустити")],
            [KeyboardButton(text="⏸ Зупинити")]
        ],
        resize_keyboard=True
    )


def settings_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏱ Встановити інтервал")],
            [KeyboardButton(text="🔎 Додати фільтр")],
            [KeyboardButton(text="🗑 Видалити фільтр")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )


def cancel():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Скасувати")]],
        resize_keyboard=True
    )


def channel_type():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📺 Джерело")],
            [KeyboardButton(text="📤 Отримувач")],
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )