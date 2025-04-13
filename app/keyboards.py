from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.languages import LANGUAGES

languages = ["Qaraqalpaq", "O'zbek", "Русский"]

async def language_set():
    kb = ReplyKeyboardBuilder()
    for language in languages:
        kb.add(KeyboardButton(text=language))
    return kb.as_markup(resize_keyboard=True)

async def main_keyboard(lang_code):
    kb = ReplyKeyboardBuilder()
    
    # Create buttons
    add_word_btn = KeyboardButton(text=LANGUAGES[lang_code]["add_word"])
    my_words_btn = KeyboardButton(text=LANGUAGES[lang_code]["my_words"])
    learned_words_btn = KeyboardButton(text=LANGUAGES[lang_code]["learned_words"])
    words_this_month_btn = KeyboardButton(text=LANGUAGES[lang_code]["words_this_month"])
    
    # Add buttons in rows of 2
    kb.row(add_word_btn, words_this_month_btn)
    kb.row(learned_words_btn, my_words_btn)
    
    return kb.as_markup(resize_keyboard=True)
