import re
import asyncio
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.requests import get_all_schedules_now, get_word_by_id, get_user_by_id, update_schedule_by_id
from app.bot import bot
from app.languages import LANGUAGES
from app.state import user_language

async def get_current_time():
    return datetime.datetime.now()


def escape_markdown(text: str) -> str:
    """
    Escapes special characters in text for Telegram MarkdownV2.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


# Asynchronous task to handle scheduled jobs
async def async_task():
    try:
        data = await get_all_schedules_now()
        time = await get_current_time()

        if not data:
            print("No schedules to process.")
        else:
            for record in data:
                word_data = await get_word_by_id(record.user_id, record.word_id)
                user_data = await get_user_by_id(record.user_id)

                if record.stage == 1:  # First repetition
                    await bot.send_message(
                        chat_id=user_data.tg_id,
                        text=(
                            f"Repeat this *{escape_markdown(word_data.word)}*\n"
                            f"Translation ||{escape_markdown(word_data.translation)}||"
                        ),
                        parse_mode="MarkdownV2"
                    )
                    # Update next repetition time to 2 minutes
                    await update_schedule_by_id(
                        record.id, record.user_id, record.word_id,
                        2, time + datetime.timedelta(minutes=60)
                    )
                elif record.stage == 2:  # Second repetition
                    await bot.send_message(
                        chat_id=user_data.tg_id,
                        text=(
                            f"Repeat this *{escape_markdown(word_data.word)}*\n"
                            f"Translation ||{escape_markdown(word_data.translation)}||"
                        ),
                        parse_mode="MarkdownV2"
                    )
                    # Optionally increase the interval further (e.g., 5 minutes)
                    await update_schedule_by_id(
                        record.id, record.user_id, record.word_id,
                        3, time + datetime.timedelta(days=1)
                    )
                elif record.stage == 3:  # Second repetition
                    await bot.send_message(
                        chat_id=user_data.tg_id,
                        text=(
                            f"Repeat this *{escape_markdown(word_data.word)}*\n"
                            f"Translation ||{escape_markdown(word_data.translation)}||"
                        ),
                        parse_mode="MarkdownV2"
                    )
                    # Optionally increase the interval further (e.g., 5 minutes)
                    await update_schedule_by_id(
                        record.id, record.user_id, record.word_id,
                        4, time + datetime.timedelta(days=2)
                    )
                elif record.stage == 4:  # Second repetition
                    await bot.send_message(
                        chat_id=user_data.tg_id,
                        text=(
                            f"Repeat this *{escape_markdown(word_data.word)}*\n"
                            f"Translation ||{escape_markdown(word_data.translation)}||"
                        ),
                        parse_mode="MarkdownV2"
                    )
                    # Optionally increase the interval further (e.g., 5 minutes)
                    await update_schedule_by_id(
                        record.id, record.user_id, record.word_id,
                        5, time + datetime.timedelta(days=6)
                    )
                elif record.stage == 5:  # Second repetition
                    await bot.send_message(
                        chat_id=user_data.tg_id,
                        text=(
                            f"Repeat this *{escape_markdown(word_data.word)}*\n"
                            f"Translation ||{escape_markdown(word_data.translation)}||"
                        ),
                        parse_mode="MarkdownV2"
                    )
                    # Optionally increase the interval further (e.g., 5 minutes)
                    await update_schedule_by_id(
                        record.id, record.user_id, record.word_id,
                        6, time + datetime.timedelta(days=12)
                    )
                else:
                    pass  # Handle further stages or stop repetitions if needed
    except Exception as e:
        print(f"Error in async_task: {e}")

    print("Async task completed.")

# Main scheduler function
async def scheduler_main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(async_task, 'interval', seconds=60)  # Check for tasks every 15 seconds
    scheduler.start()

    print("Scheduler started. Running in background.")
    while True:
        await asyncio.sleep(3600)  # Keep the scheduler alive and prevent exit
