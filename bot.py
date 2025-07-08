import asyncio
import os
import json
from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from config import TOKEN
from commands import START_COMMAND, READ_COMMAND, MY_READS_COMMAND, DETECTIVES_COMMAND, ROMANCE_COMMAND, FANTASY_COMMAND, FICTION_COMMAND, HORROR_COMMAND, COMICS_COMMAND, POETRY_COMMAND, WAR_PROSE_COMMAND, HISTORICAL_NOVELS_COMMAND, WOMEN_PROSE_COMMAND, NON_FICTION_COMMAND, ESOTERICS_COMMAND, DELETE_COMMAND
from commands import BOOK_DETECTIVE_CREATE_COMMAND, BOOK_ROMANCE_CREATE_COMMAND, BOOK_FANTASY_CREATE_COMMAND, BOOK_FICTION_CREATE_COMMAND, BOOK_HORROR_CREATE_COMMAND, BOOK_COMICS_CREATE_COMMAND, BOOK_POETRY_CREATE_COMMAND, BOOK_HISTORICAL_NOVELS_CREATE_COMMAND, BOOK_WAR_PROSE_CREATE_COMMAND, BOOK_WOMEN_PROSE_CREATE_COMMAND, BOOK_NON_FICTION_CREATE_COMMAND, BOOK_ESOTERICS_CREATE_COMMAND
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import Book
from data import get_book, add_book, CATEGORY_ID_MAP
from keyboard import books_keyboard_markup
from aiogram.types import FSInputFile
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
#FSM для створення книги
class BookForm(StatesGroup):
    name = State()
    author = State()
    year_of_publication = State()
    publishing_house = State()
    number_of_pages = State()
    description = State()
    cover_image = State()
#FSM для створення власного списку збереж книг
class ReadStates(StatesGroup):
    await_book_name = State()
    await_rating = State()
    await_review = State()
#Вітання
@dp.message(START_COMMAND)
async def start(message: Message):
    await message.answer(
        f"Вітаннячко, {message.from_user.username}!\nКнижковий порадник – твій кишеньковий бібліотекар.\n\n"
        f"Щоб почати пошук, оберіть команду з бажаним жанром книги:\n"
        f"<b>ХУДОЖНЯ ЛІТЕРАТУРА</b>:\n"
        f"/detectives - детективи\n"
        f"/romance - любовні романи\n"
        f"/fantasy - фантастика\n"
        f"/fiction - фентезі\n"
        f"/horror - жахи, трилери\n"
        f"/comics - комікси\n"
        f"/poetry - поезія\n"
        f"/war_prose - воєнна проза\n"
        f"/historical_novels - історичні романи\n"
        f"/women_prose - жіноча проза\n"
        f"<b>НЕХУДОЖНЯ ЛІТЕРАТУРА</b>:\n"
        f"/non_fiction - нон-фікшн\n"
        f"/esoterics - ізотерика\n\n"
        f"Щоб додати книгу введіть команду: /book_..._create (на місці трьох крапок напишіть бажаний жанр)")
#Команди перегляду книжок за жанрами
GENRE_COMMANDS = {
    DETECTIVES_COMMAND: "detective",
    ROMANCE_COMMAND: "romance",
    FANTASY_COMMAND: "fantasy",
    FICTION_COMMAND: "fiction",
    HORROR_COMMAND: "horror",
    COMICS_COMMAND: "comics",
    POETRY_COMMAND: "poetry",
    HISTORICAL_NOVELS_COMMAND: "historical_novels",
    WAR_PROSE_COMMAND: "war_prose",
    WOMEN_PROSE_COMMAND: "women_prose",
    NON_FICTION_COMMAND: "non_fiction",
    ESOTERICS_COMMAND: "esoteric"
}
for command, category in GENRE_COMMANDS.items():
    @dp.message(command)
    async def send_books(message: Message, category=category):
        books = get_book(category)
        await message.answer(
            f"Ось наявні книги у жанрі: {category.title()}",
            reply_markup=books_keyboard_markup(books, category)
        )
#Обробка callback_data
@dp.callback_query(lambda c: ":" in c.data and not c.data.startswith("read:"))
async def handle_book_callback(callback: CallbackQuery):
    try:
        category, index_str = callback.data.split(":")
        index = int(index_str)
        books = get_book(category)
        book_data = books[index]
        book = Book(**book_data)
        text = (
            f"<b>Назва книги:</b> {book.name}\n" \
            f"<b>Автор:</b> {book.author}\n" \
            f"<b>Рік видання:</b> {book.year_of_publication}\n" \
            f"<b>Видавництво:</b> {book.publishing_house}\n" \
            f"<b>Кількість сторінок:</b> {book.number_of_pages}\n" \
            f"<b>Анотація:</b> {book.description}\n"
        )
        image_path = os.path.join("images", book.cover_image or "")
        if os.path.exists(image_path):
            await asyncio.sleep(0.5)
            photo = FSInputFile(image_path)
            await callback.message.answer_photo(photo=photo, caption=text)
        else:
            await callback.message.answer(text + "\n(Обкладинка не знайдена)")
    except Exception as e:
        print(f"Callback error: {e}")
        await callback.message.answer("Сталася помилка при показі книги.")
#Створення книг
CREATE_COMMANDS = {
    BOOK_DETECTIVE_CREATE_COMMAND: "detective",
    BOOK_ROMANCE_CREATE_COMMAND: "romance",
    BOOK_FANTASY_CREATE_COMMAND: "fantasy",
    BOOK_FICTION_CREATE_COMMAND: "fiction",
    BOOK_HORROR_CREATE_COMMAND: "horror",
    BOOK_COMICS_CREATE_COMMAND: "comics",
    BOOK_POETRY_CREATE_COMMAND: "poetry",
    BOOK_HISTORICAL_NOVELS_CREATE_COMMAND: "historical_novels",
    BOOK_WAR_PROSE_CREATE_COMMAND: "war_prose",
    BOOK_WOMEN_PROSE_CREATE_COMMAND: "women_prose",
    BOOK_NON_FICTION_CREATE_COMMAND: "non_fiction",
    BOOK_ESOTERICS_CREATE_COMMAND: "esoteric"
}
for command, category in CREATE_COMMANDS.items():
    @dp.message(command)
    async def create_book_entry(message: Message, state: FSMContext, category=category):
        await state.set_state(BookForm.name)
        await state.update_data(category=category)
        await message.answer("Введіть назву книги", reply_markup=ReplyKeyboardRemove())
@dp.message(BookForm.name)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookForm.author)
    await message.answer("Введіть ім’я та прізвище автора")
@dp.message(BookForm.author)
async def step_author(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await state.set_state(BookForm.year_of_publication)
    await message.answer("Введіть рік видання")
@dp.message(BookForm.year_of_publication)
async def step_year(message: Message, state: FSMContext):
    await state.update_data(year_of_publication=message.text)
    await state.set_state(BookForm.publishing_house)
    await message.answer("Введіть назву видавництва")
@dp.message(BookForm.publishing_house)
async def step_publisher(message: Message, state: FSMContext):
    await state.update_data(publishing_house=message.text)
    await state.set_state(BookForm.number_of_pages)
    await message.answer("Введіть кількість сторінок")
@dp.message(BookForm.number_of_pages)
async def step_pages(message: Message, state: FSMContext):
    await state.update_data(number_of_pages=message.text)
    await state.set_state(BookForm.description)
    await message.answer("Введіть опис книги")
@dp.message(BookForm.description)
async def step_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(BookForm.cover_image)
    await message.answer("Надішліть, будь ласка, обкладинку книги (фото)")
@dp.message(BookForm.cover_image)
async def step_cover_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_name = f"{message.from_user.id}_{photo.file_unique_id}.jpg"
    file_path = os.path.join("images", file_name)
    await message.bot.download_file(file.file_path, destination=file_path)
    await state.update_data(cover_image=file_name)
    data = await state.get_data()
    book = Book(**data)
    add_book(book.model_dump(), data["category"])
    await state.clear()
    await message.answer("Книгу збережено")
# Клавіатура жанрів
GENRE_NAMES = {
    "detective": "Детективи",
    "fantasy": "Фантастика",
    "romance": "Любовні романи",
    "fiction": "Фентезі",
    "horror": "Трилери",
    "comics": "Комікси",
    "poetry": "Поезія",
    "war_prose": "Воєнна проза",
    "historical_novels": "Історичні романи",
    "women_prose": "Жіноча проза",
    "non_fiction": "Нон-фікшн",
    "esoteric": "Езотерика"
}
# Команда /read
@dp.message(Command("read"))
async def start_read_command(message: Message, state: FSMContext):
    await message.answer("Оберіть жанр, у якому прочитана вами книга:", reply_markup=get_genre_keyboard())
def get_genre_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, name in GENRE_NAMES.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"genre:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
@dp.callback_query(F.data.startswith("genre:"))
async def handle_genre_selection(callback: CallbackQuery, state: FSMContext):
    genre = callback.data.split(":")[1]
    books = get_book(genre)
    if not books:
        await callback.message.answer("У цьому жанрі поки немає книг.")
        return
    await state.update_data(selected_category=genre)
    await callback.message.answer(
        f"Книги в жанрі: {genre.title()}",
        reply_markup=get_book_keyboard(genre)
    )
    await callback.answer()
def get_book_keyboard(category: str) -> InlineKeyboardMarkup:
    books = get_book(category)
    buttons = []
    for idx, book in enumerate(books):
        buttons.append([InlineKeyboardButton(
            text=book["name"],
            callback_data=f"read:{category}:{idx}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
@dp.callback_query(F.data.startswith("read:"))
async def handle_read_callback(callback: CallbackQuery, state: FSMContext):
    try:
        print(f" callback.data = {callback.data}")
        _, genre, index_str = callback.data.split(":")
        index = int(index_str)
        books = get_book(genre)
        if index >= len(books):
            await callback.message.answer("Книгу не знайдено ")
            return
        book = books[index]
        await state.update_data(
            selected_category=genre,
            book_name=book["name"]
        )
        await callback.message.answer(
            f"Обрана книга: «{book['name']}». Що хочеш зробити?",
            reply_markup=get_read_action_keyboard()
        )
    except Exception as e:
        print(f"[!] Помилка read-callback: {e}")
        await callback.message.answer("Сталася помилка при обробці книги.")
    await callback.answer()
@dp.callback_query(F.data == "rate")
async def handle_rate(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введіть оцінку від 1 до 5:")
    await state.set_state(ReadStates.await_rating)
    await callback.answer()
@dp.callback_query(F.data == "comment")
async def handle_comment(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишіть свій коментар:")
    await state.set_state(ReadStates.await_review)
    await callback.answer()
@dp.callback_query(F.data == "confirm_read")
async def handle_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_user_book(callback.from_user.id, data["book_name"], data.get("rating", None), data.get("review", ""))
    await state.clear()
    await callback.message.answer("Книгу додано до прочитаного!")
    await callback.answer()
@dp.message(ReadStates.await_rating)
async def receive_rating(message: Message, state: FSMContext):
    try:
        rating = int(message.text)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        await message.answer("Введіть число від 1 до 5.")
        return
    await state.update_data(rating=rating)
    await message.answer("Тепер напишіть короткий відгук:")
    await state.set_state(ReadStates.await_review)
@dp.message(ReadStates.await_review)
async def receive_review(message: Message, state: FSMContext):
    review = message.text
    data = await state.get_data()
    add_user_book(
        message.from_user.id,
        data["book_name"],
        data.get("rating", None),
        review
    )
    await state.clear()
    await message.answer("Готово! Книгу додано до списку прочитаного.")
# /my_reads
@dp.message(Command("my_reads"))
async def show_my_reads(message: Message):
    books = get_user_books(message.from_user.id)
    if not books:
        await message.answer("У вас ще немає прочитаних книг.")
        return
    text = "<b>Ваші прочитані книги:</b>\n\n"
    for b in books:
        text += (
            f"📖 <u>{b['name']}</u>\n"
            f"Оцінка: ⭐ {b['rating']}/5\n"
            f"Відгук: {b['review']}\n\n"
        )
    await message.answer(text)
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())