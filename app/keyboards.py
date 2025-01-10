from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.languages import LANGUAGES

languages = ["Qaraqalpaq", "O'zbek", "Русский"]

# Function to generate the language selection keyboard
async def language_set():
    keyboard = ReplyKeyboardBuilder()
    for language in languages:
        keyboard.add(KeyboardButton(text=language))
    return keyboard.adjust(3).as_markup(resize_keyboard=True)

# Function to generate the main keyboard dynamically based on the selected language
async def main_keyboard(lang_code):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=LANGUAGES[lang_code]["add_word"])],
        [KeyboardButton(text=LANGUAGES[lang_code]["my_words"])]
    ], resize_keyboard=True)
