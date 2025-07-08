from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#Створює клавіатуру з коротким callback_data: category:index
def books_keyboard_markup(books: list[dict], category: str) -> InlineKeyboardMarkup:
    keyboard = []
    for idx, book in enumerate(books):
        keyboard.append([
            InlineKeyboardButton(
                text=book["name"],
                callback_data=f"{category}:{idx}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
