import json
import os
#Всі доступні категорії та їх відповідні JSON-файли
BOOK_PATHS = {
    "detective": "data.json",
    "romance": "data1.json",
    "fantasy": "data2.json",
    "fiction": "data3.json",
    "horror": "data4.json",
    "comics": "data5.json",
    "poetry": "data6.json",
    "historical_novels": "data7.json",
    "war_prose": "data8.json",
    "women_prose": "data9.json",
    "non_fiction": "data10.json",
    "esoteric": "data11.json"
}
CATEGORY_ID_MAP = {
    "1": "detective",
    "2": "romance",
    "3": "fantasy",
    "4": "fiction",
    "5": "horror",
    "6": "comics",
    "7": "poetry",
    "8": "historical_novels",
    "9": "war_prose",
    "10": "women_prose",
    "11": "non_fiction",
    "12": "esoteric"
}
#Автоматичне створення порожнього JSON, якщо його не існує
def ensure_file(file: str):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as fp:
            json.dump([], fp, indent=4, ensure_ascii=False)
#Загальна функція для читання книг з категорії
def get_book(category: str) -> list[dict]:
    file = BOOK_PATHS.get(category)
    if not file:
        raise ValueError(f"Категорія '{category}' не знайдена.")
    ensure_file(file)
    with open(file, "r", encoding="utf-8") as fp:
        return json.load(fp)
#Загальна функція для додавання книги до категорії
def add_book(book: dict, category: str) -> None:
    file = BOOK_PATHS.get(category)
    if not file:
        raise ValueError(f"Категорія '{category}' не знайдена.")
    books = get_book(category)
    books.append(book)
    with open(file, "w", encoding="utf-8") as fp:
        json.dump(books, fp, indent=4, ensure_ascii=False)
#Автоматичне створення get_books() і add_book() функцій
for key in BOOK_PATHS:
    globals()[f"get_book_{key}"] = (lambda k=key: get_book(k))
    globals()[f"add_book_{key}"] = (lambda book, k=key: add_book(book, k))