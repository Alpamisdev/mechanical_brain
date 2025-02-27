from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import datetime
from app import keyboards as kb
from app.database import requests as rq
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.languages import LANGUAGES
from app.state import user_language


router = Router()

class FMessage(StatesGroup):
    fmessage = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.full_name)
    await message.answer("Tildi tańlań / Tilni tanlang / Выбирайте язык:", reply_markup=await kb.language_set())

@router.message(Command('fm'))
async def get_forward_message(message: Message, state: FSMContext):
    await state.set_state(FMessage.fmessage)
    await message.answer('Send Post')

@router.message(FMessage.fmessage)
async def forward_message(message: Message, state: FSMContext):
    users = await rq.get_all_users()
    k = 0
    for user in users:
        await message.forward(chat_id=user.tg_id)
        k += 1
    await message.answer(f'Succes! Post sent for {k} users')
    await state.clear()

# Handle language selection
@router.message(lambda message: message.text in ["Qaraqalpaq", "O'zbek", "Русский"])
async def set_language(message: Message):
    # Map user choice to language code
    lang_code = {"Qaraqalpaq": "kaa", "O'zbek": "uz", "Русский": "ru"}[message.text]
    user_language[message.from_user.id] = lang_code  # Store user's language preference

    # Respond in the selected language
    await message.answer(LANGUAGES[lang_code]["language_set"], reply_markup=await kb.main_keyboard(lang_code))

# Add Word
class AddWord(StatesGroup):
    word = State()
    translation = State()

# Add Word (Handler for the "add_word" button)
@router.message(Command('neword'))
@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["add_word"],
    LANGUAGES["uz"]["add_word"],
    LANGUAGES["ru"]["add_word"]
])
async def add_word(message: Message, state: FSMContext):
    # Get user's language preference
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set
    await state.set_state(AddWord.word)
    await message.answer(LANGUAGES[lang_code]["add_word_prompt"])

@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["my_words"],
    LANGUAGES["uz"]["my_words"],
    LANGUAGES["ru"]["my_words"]
])
async def my_words(message: Message):
    user = message.from_user.id
    words = await rq.get_words_by_user(user)
    message_to_send = ""
    k = 0
    for word in words:
        k += 1
        message_to_send += f"\n{k}) {word.word}"
    await message.answer(message_to_send)

@router.message(AddWord.word)
async def add_translation(message: Message, state: FSMContext):
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set

    new_word = str.lower(message.text)
    await state.update_data(word=new_word)
    await state.set_state(AddWord.translation)
    await message.answer(LANGUAGES[lang_code]["add_word_translate"])

@router.message(AddWord.translation)
async def word_to_db(message: Message, state: FSMContext):
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set

    new_word = str.lower(message.text)
    await state.update_data(translation=new_word)
    user = await rq.get_user(message.from_user.id)
    data = await state.get_data()

    # Ensure the word is added and check if it already exists
    is_exists = await rq.set_word(user.id, data['word'], data['translation'])
    
    if not is_exists:
        await message.answer(f'{LANGUAGES[lang_code]["word_allradey_excist"]}')
        await state.clear()
    else:
        
        await message.answer(f'{user.name} - {LANGUAGES[lang_code]["word_added"]}.\n{data["word"]} - {data["translation"]}\nFor adding new word command \\neword')
        
        # Make sure to get the word_id after adding it to the database
        word_id = await rq.get_word(user.id, data['word'])
        
        if word_id:
            # Set the initial schedule (next review in 2 minutes)
            await rq.set_schedule(user.id, word_id, 1, datetime.datetime.now() + datetime.timedelta(minutes=20))
        else:
            await message.answer(f'{LANGUAGES[lang_code]["word_not_found"]}')
        
        await state.clear()


