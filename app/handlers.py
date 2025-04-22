from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import datetime, asyncio
from app import keyboards as kb
from app.database import requests as rq
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.languages import LANGUAGES
from app.state import user_language
from app.utils import split_long_message
from app.utils.generate_report import generate_user_growth_chart, generate_activity_heatmap, generate_monthly_report
from app.scheduler import async_task  # Import async_task from scheduler.py


router = Router()

class FMessage(StatesGroup):
    fmessage = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Start a new session when user starts the bot
    await rq.start_user_session(message.from_user.id)
    await rq.log_command(message.from_user.id, "/start")

    text = (
        "🌟 <b>Welcome!</b> 🌟\n\n"
        
        "🇬🇧 <b>English:</b>\n"
        '"Hello! This bot will help you learn new words efficiently and remember them for a long time using the Ebbinghaus method."\n\n'

        "🇺🇿 <b>O‘zbekcha:</b>\n"
        '"Salom! Ushbu bot sizga yangi so‘zlarni samarali o‘rganishga va Ebbinghaus metodi orqali ularni yodda saqlashga yordam beradi."\n\n'

        "🇷🇺 <b>Русский:</b>\n"
        '"Привет! Этот бот поможет вам эффективно учить новые слова и запоминать их с помощью метода Эббингауза."\n\n'
        
        "🌍 <b>Qaraqalpaqsha:</b>\n"
        '"Sálem! Bul bot sizge jańa sózlerdi nátiyjeli úyreniwge hám Ebbinghaus metodı menen eslewge járdem beredi."\n\n'
        
        "📖 <b>Instructions:</b>\n"
        "📌 <b>Instruction for Using the Telegram Bot</b>\n"
        '<a href="https://telegra.ph/Instruction-for-Using-the-Telegram-Bot-to-Memorize-Words-03-09">English</a>\n\n'
        
        "📌 <b>Telegram botdan foydalanish bo'yicha qo'llanma</b>\n"
        '<a href="https://telegra.ph/Sozlarni-yodlash-uchun-Telegram-botidan-foydalanish-boyicha-qollanma-03-09">O\'zbek</a>\n\n'
        
        "📌 <b>Инструкция по использованию Telegram-бота</b>\n"
        '<a href="https://telegra.ph/Instrukciya-po-ispolzovaniyu-Telegram-bota-dlya-zapominaniya-slov-03-09">Русский</a>\n\n'
        
        "📌 <b>Telegram bottan paydalanıw qollanbası</b>\n"
        '<a href="https://telegra.ph/Telegram-bot-qollanbas%C4%B1-03-03">Qaraqalpaq</a>\n\n'
        
        "🚀 <b>Let’s make learning fun and effective!</b> 🚀"
    )
    await rq.set_user(message.from_user.id, message.from_user.full_name)

    await message.answer(
        text=text,
        parse_mode="HTML"
    )
    await message.answer("Tildi tańlań / Tilni tanlang / Выбирайте язык:", reply_markup=await kb.language_set())

@router.message(Command('help'))
async def cmd_help(message: Message):

    text = (
        "🌟 <b>Welcome!</b> 🌟\n\n"
        
        "🇬🇧 <b>English:</b>\n"
        '"Hello! This bot will help you learn new words efficiently and remember them for a long time using the Ebbinghaus method."\n\n'

        "🇺🇿 <b>O‘zbekcha:</b>\n"
        '"Salom! Ushbu bot sizga yangi so‘zlarni samarali o‘rganishga va Ebbinghaus metodi orqali ularni yodda saqlashga yordam beradi."\n\n'

        "🇷🇺 <b>Русский:</b>\n"
        '"Привет! Этот бот поможет вам эффективно учить новые слова и запоминать их с помощью метода Эббингауза."\n\n'
        
        "🌍 <b>Qaraqalpaqsha:</b>\n"
        '"Sálem! Bul bot sizge jańa sózlerdi nátiyjeli úyreniwge hám Ebbinghaus metodı menen eslewge járdem beredi."\n\n'
        
        "📖 <b>Instructions:</b>\n"
        "📌 <b>Instruction for Using the Telegram Bot</b>\n"
        '<a href="https://telegra.ph/Instruction-for-Using-the-Telegram-Bot-to-Memorize-Words-03-09">English</a>\n\n'
        
        "📌 <b>Telegram botdan foydalanish bo'yicha qo'llanma</b>\n"
        '<a href="https://telegra.ph/Sozlarni-yodlash-uchun-Telegram-botidan-foydalanish-boyicha-qollanma-03-09">O\'zbek</a>\n\n'
        
        "📌 <b>Инструкция по использованию Telegram-бота</b>\n"
        '<a href="https://telegra.ph/Instrukciya-po-ispolzovaniyu-Telegram-bota-dlya-zapominaniya-slov-03-09">Русский</a>\n\n'
        
        "📌 <b>Telegram bottan paydalanıw qollanbası</b>\n"
        '<a href="https://telegra.ph/Telegram-bot-qollanbas%C4%B1-03-03">Qaraqalpaq</a>\n\n'
        
        "🚀 <b>Let’s make learning fun and effective!</b> 🚀"
    )

    await message.answer(
        text=text,
        parse_mode="HTML"
    )

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
        
        await message.answer(f'{user.name} - {LANGUAGES[lang_code]["word_added"]}.\n{data["word"]} - {data["translation"]}\nFor adding new word command /neword')
        
        # Make sure to get the word_id after adding it to the database
        word_id = await rq.get_word(user.id, data['word'])
        
        if word_id:
            await rq.set_schedule(user.id, word_id, 1, datetime.datetime.now() + datetime.timedelta(minutes=1))
        else:
            await message.answer(f'{LANGUAGES[lang_code]["word_not_found"]}')
        
        await state.clear()


# code of v0
@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["learned_words"],
    LANGUAGES["uz"]["learned_words"],
    LANGUAGES["ru"]["learned_words"]
])
async def learned_words(message: Message):
    """Handler for the 'Learned Words' button"""
    user = message.from_user.id
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set
    
    # Get user ID from tg_id
    user_data = await rq.get_user(user)
    if not user_data:
        return
    
    # Get learned words (stage >= 7)
    words = await rq.get_learned_words(user_data.id)
    
    if not words or len(words) == 0:
        await message.answer(LANGUAGES[lang_code]["no_learned_words"])
        return
    
    # Format the message
    message_to_send = f"🎓 {LANGUAGES[lang_code]['learned_words']}:\n"
    for i, word in enumerate(words, 1):
        message_to_send += f"\n{i}) {word.word} - {word.translation}"
    
    # Split the message if it's too long
    message_parts = split_long_message(message_to_send)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part)

@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["words_this_month"],
    LANGUAGES["uz"]["words_this_month"],
    LANGUAGES["ru"]["words_this_month"]
])
async def words_this_month(message: Message):
    """Handler for the 'Words Added This Month' button"""
    user = message.from_user.id
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set
    
    # Get user ID from tg_id
    user_data = await rq.get_user(user)
    if not user_data:
        return
    
    # Get words added this month
    words = await rq.get_words_added_this_month(user_data.id)
    
    if not words or len(words) == 0:
        await message.answer(LANGUAGES[lang_code]["no_words_this_month"])
        return
    
    # Format the message
    count = len(words)
    message_to_send = f"📅 {LANGUAGES[lang_code]['words_added_this_month'].format(count=count)}:\n"
    
    for i, word in enumerate(words, 1):
        message_to_send += f"\n{i}) {word.word} - {word.translation}"
    
    # Split the message if it's too long
    message_parts = split_long_message(message_to_send)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part)

# Also update the my_words handler to use the same approach
@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["my_words"],
    LANGUAGES["uz"]["my_words"],
    LANGUAGES["ru"]["my_words"]
])
async def my_words(message: Message):
    user = message.from_user.id
    words = await rq.get_words_by_user(user)
    
    if not words or len(words) == 0:
        lang_code = user_language.get(message.from_user.id, "kaa")
        await message.answer(LANGUAGES[lang_code]["word_not_found"])
        return
        
    message_to_send = ""
    k = 0
    for word in words:
        k += 1
        message_to_send += f"\n{k}) {word.word} - {word.translation}"
    
    # Split the message if it's too long
    message_parts = split_long_message(message_to_send)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part)
        
@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["learned_words"],
    LANGUAGES["uz"]["learned_words"],
    LANGUAGES["ru"]["learned_words"]
])
async def learned_words(message: Message):
    """Handler for the 'Learned Words' button"""
    user = message.from_user.id
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set
    
    # Log this as a command
    await rq.log_command(user, "learned_words")
    
    # Update user activity
    await rq.update_user_activity(user)
    
    # Rest of the existing code...
    # Get user ID from tg_id
    user_data = await rq.get_user(user)
    if not user_data:
        return
    
    # Get learned words (stage >= 7)
    words = await rq.get_learned_words(user_data.id)
    
    if not words or len(words) == 0:
        await message.answer(LANGUAGES[lang_code]["no_learned_words"])
        return
    
    # Format the message
    message_to_send = f"🎓 {LANGUAGES[lang_code]['learned_words']}:\n"
    for i, word in enumerate(words, 1):
        message_to_send += f"\n{i}) {word.word} - {word.translation}"
    
    # Split the message if it's too long
    message_parts = split_long_message(message_to_send)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part)

@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["words_this_month"],
    LANGUAGES["uz"]["words_this_month"],
    LANGUAGES["ru"]["words_this_month"]
])
async def words_this_month(message: Message):
    """Handler for the 'Words Added This Month' button"""
    user = message.from_user.id
    lang_code = user_language.get(message.from_user.id, "kaa")  # Default to "kaa" if not set
    
    # Get user ID from tg_id
    user_data = await rq.get_user(user)
    if not user_data:
        return
    
    # Get words added this month
    words = await rq.get_words_added_this_month(user_data.id)
    
    if not words or len(words) == 0:
        await message.answer(LANGUAGES[lang_code]["no_words_this_month"])
        return
    
    # Format the message
    count = len(words)
    message_to_send = f"📅 {LANGUAGES[lang_code]['words_added_this_month'].format(count=count)}:\n"
    
    for i, word in enumerate(words, 1):
        message_to_send += f"\n{i}) {word.word} - {word.translation}"
    
    # Split the message if it's too long
    message_parts = split_long_message(message_to_send)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part)

# Also update the my_words handler to use the same approach
@router.message(lambda message: message.text and message.text in [
    LANGUAGES["kaa"]["my_words"],
    LANGUAGES["uz"]["my_words"],
    LANGUAGES["ru"]["my_words"]
])
async def my_words(message: Message):
    user = message.from_user.id
    words = await rq.get_words_by_user(user)
    
    if not words or len(words) == 0:
        lang_code = user_language.get(message.from_user.id, "kaa")
        await message.answer(LANGUAGES[lang_code]["word_not_found"])
        return
        
    message_to_send = ""
    k = 0
    for word in words:
        k += 1
        message_to_send += f"\n{k}) {word.word} - {word.translation}"
    
    # Split the message if it's too long
    message_parts = split_long_message(message_to_send)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part)

# @router.message(Command('stats'))
# async def get_statistics(message: Message):
#     """Handler for the /stats command - shows basic bot statistics"""
#     # Check if user is an admin (you can add admin IDs to a list or env variable)
#     admin_ids = [1672596043]  # Added the current user for testing
    
#     if message.from_user.id not in admin_ids:
#         await message.answer("You don't have permission to view statistics.")
#         return
    
#     await rq.log_command(message.from_user.id, "/stats")
    
#     # Get statistics
#     stats = await rq.get_comprehensive_statistics()
    
#     # Format the message - using HTML instead of Markdown for better compatibility
#     stats_message = (
#         "<b>📊 Bot Statistics 📊</b>\n\n"
#         "<b>👥 User Metrics</b>\n"
#         f"• Total Users: {stats['total_users']}\n"
#         f"• Daily Active Users: {stats['daily_active_users']}\n"
#         f"• Weekly Active Users: {stats['weekly_active_users']}\n"
#         f"• Monthly Active Users: {stats['monthly_active_users']}\n"
#         f"• Retention Rate: {stats['retention_rate']:.2f}%\n\n"
        
#         "<b>📚 Word Metrics</b>\n"
#         f"• Total Words: {stats['total_words']}\n"
#         f"• Words Added Today: {stats['words_added_today']}\n"
#         f"• Words Added This Month: {stats['words_added_this_month']}\n"
#         f"• Total Learned Words: {stats['total_learned_words']}\n"
#         f"• Average Words Per User: {stats['avg_words_per_user']:.2f}\n\n"
        
#         "<b>⏱ Engagement Metrics</b>\n"
#         f"• Average Session Length: {stats['avg_session_minutes']:.2f} minutes\n"
#     )
    
#     # Add most popular commands if available
#     if stats['popular_commands']:
#         stats_message += "\n<b>📋 Most Popular Commands</b>\n"
#         for cmd, count in stats['popular_commands']:
#             stats_message += f"• {cmd}: {count} uses\n"
    
#     # Add most active users if available
#     if stats['most_active_users']:
#         stats_message += "\n<b>🏆 Most Active Users</b>\n"
#         for tg_id, name, count in stats['most_active_users']:
#             # Escape HTML special characters in user names
#             safe_name = name.replace('<', '&lt;').replace('>', '&gt;') if name else "Unknown"
#             stats_message += f"• {safe_name}: {count} commands\n"
    
#     # Split the message if it's too long
#     message_parts = split_long_message(stats_message)
    
#     # Send each part as a separate message
#     for part in message_parts:
#         await message.answer(part, parse_mode="HTML")

# @router.message(Command('period_stats'))
# async def get_period_statistics(message: Message):
#     """Handler for the /detailed_stats command - shows detailed statistics with graphs"""
#     # Check if user is an admin
#     admin_ids = [1672596043]  # Added the current user for testing
    
#     if message.from_user.id not in admin_ids:
#         await message.answer("You don't have permission to view detailed statistics.")
#         return
    
#     await rq.log_command(message.from_user.id, "/detailed_stats")
    
#     # Get statistics
#     stats = await rq.get_comprehensive_statistics()
    
#     # Format user growth data - using HTML instead of Markdown
#     user_growth_message = "<b>👥 User Growth (Last 7 Days)</b>\n"
#     for date, count in stats['user_growth']:
#         user_growth_message += f"• {date.strftime('%Y-%m-%d')}: {count} new users\n"
    
#     # Format word growth data
#     word_growth_message = "<b>📚 Word Growth (Last 7 Days)</b>\n"
#     for date, count in stats['word_growth']:
#         word_growth_message += f"• {date.strftime('%Y-%m-%d')}: {count} new words\n"
    
#     # Format hour activity data
#     hour_activity_message = "<b>⏰ Activity by Hour of Day</b>\n"
#     for hour, count in stats['hour_activity']:
#         hour_activity_message += f"• {int(hour):02d}:00: {count} commands\n"
    
#     # Combine all detailed stats
#     detailed_stats_message = (
#         "<b>📊 Detailed Bot Statistics 📊</b>\n\n" +
#         user_growth_message + "\n" +
#         word_growth_message + "\n" +
#         hour_activity_message
#     )
    
#     # Split the message if it's too long
#     message_parts = split_long_message(detailed_stats_message)
    
#     # Send each part as a separate message
#     for part in message_parts:
#         await message.answer(part, parse_mode="HTML")


# @router.message(Command('visual_stats'))
# async def get_visual_statistics(message: Message):
#     """Handler for the /visual_stats command - generates and sends visual statistics"""
#     # Check if user is an admin
#     admin_ids = [1672596043]  # Replace with actual admin IDs
    
#     if message.from_user.id not in admin_ids:
#         await message.answer("You don't have permission to view visual statistics.")
#         return
    
#     await rq.log_command(message.from_user.id, "/visual_stats")
#     await message.answer("Generating visual statistics... This may take a moment.")
    
#     # Get statistics
#     stats = await rq.get_comprehensive_statistics()
    
#     # Generate charts
#     user_growth_chart = await generate_user_growth_chart(stats['user_growth'])
#     activity_heatmap = await generate_activity_heatmap(stats['hour_activity'])
#     monthly_report = await generate_monthly_report(stats)
    
#     # Send charts
#     if user_growth_chart:
#         await message.answer_photo(
#             FSInputFile(user_growth_chart, filename="user_growth.png"),
#             caption="User Growth Over Time (Last 7 Days)"
#         )
    
#     if activity_heatmap:
#         await message.answer_photo(
#             FSInputFile(activity_heatmap, filename="activity_heatmap.png"),
#             caption="Activity by Hour of Day"
#         )
    
#     if monthly_report:
#         await message.answer_photo(
#             FSInputFile(monthly_report, filename="monthly_report.png"),
#             caption="Monthly Statistics Report"
#         )
    
#     await message.answer("Visual statistics generated successfully.")

# @router.message(Command('export_stats'))
# async def export_statistics(message: Message):
#     """Handler for the /export_stats command - exports statistics as CSV"""
#     # Check if user is an admin
#     admin_ids = [1672596043]  # Replace with actual admin IDs
    
#     if message.from_user.id not in admin_ids:
#         await message.answer("You don't have permission to export statistics.")
#         return
    
#     await rq.log_command(message.from_user.id, "/export_stats")
#     await message.answer("Generating statistics export... This may take a moment.")
    
#     # Get statistics
#     stats = await rq.get_comprehensive_statistics()
    
#     # Create CSV content
#     csv_content = "Metric,Value\n"
#     csv_content += f"Total Users,{stats['total_users']}\n"
#     csv_content += f"Daily Active Users,{stats['daily_active_users']}\n"
#     csv_content += f"Weekly Active Users,{stats['weekly_active_users']}\n"
#     csv_content += f"Monthly Active Users,{stats['monthly_active_users']}\n"
#     csv_content += f"Total Words,{stats['total_words']}\n"
#     csv_content += f"Words Added Today,{stats['words_added_today']}\n"
#     csv_content += f"Words Added This Month,{stats['words_added_this_month']}\n"
#     csv_content += f"Total Learned Words,{stats['total_learned_words']}\n"
#     csv_content += f"Average Words Per User,{stats['avg_words_per_user']:.2f}\n"
#     csv_content += f"Average Session Minutes,{stats['avg_session_minutes']:.2f}\n"
#     csv_content += f"Retention Rate,{stats['retention_rate']:.2f}%\n"
    
#     # Write to file
#     with open("bot_statistics.csv", "w") as f:
#         f.write(csv_content)
    
#     # Send file
#     await message.answer_document(
#         FSInputFile("bot_statistics.csv", filename="bot_statistics.csv"),
#         caption="Bot Statistics Export"
#     )

# # Add a function to update daily statistics
# async def update_daily_stats():
#     """Update daily statistics - to be called by scheduler"""
#     await rq.update_daily_statistics()

# # Add a function to track user sessions
# async def track_user_sessions():
#     """End inactive sessions - to be called by scheduler"""
#     # Get all users with active sessions
#     # End sessions for users who haven't been active for more than 30 minutes
#     # This would require additional database functions
#     pass

# # Update the scheduler_main function to include these new tasks
# async def scheduler_main():
#     scheduler = AsyncIOScheduler()
    
#     # Existing tasks
#     scheduler.add_job(async_task, 'interval', seconds=60)
    
#     # New tasks
#     scheduler.add_job(update_daily_stats, 'cron', hour=0, minute=0)  # Run at midnight
#     scheduler.add_job(track_user_sessions, 'interval', minutes=15)  # Check every 15 minutes
    
#     scheduler.start()
    
#     print("Scheduler started. Running in background.")
#     while True:
#         await asyncio.sleep(3600)  # Keep the scheduler running

# # Add middleware to track all message handlers
# @router.message()
# async def track_all_messages(message: Message, state: FSMContext):
#     """Track all messages to update user activity"""
#     await rq.update_user_activity(message.from_user.id)
    
#     # If this is a command, log it
#     if message.text and message.text.startswith('/'):
#         await rq.log_command(message.from_user.id, message.text)
    
#     # Continue processing with other handlers
#     return None
