import re
import asyncio
import datetime
import logging
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database.requests import get_all_schedules_now, get_word_by_id, get_user_by_id, update_schedule_by_id
from app.bot import bot

async def get_current_time():
    return datetime.datetime.now()

def escape_markdown(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

async def async_task():
    try:
        data = await get_all_schedules_now()
        time = await get_current_time()

        if not data:
            print("No schedules to process.")
        else:
            for record in data:
                try:
                    # Stop repeating if stage is 6 or higher
                    if record.stage >= 6:
                        # print(f"Skipping word {record.word_id} for user {record.user_id} (Stage {record.stage})")
                        continue  # Move to the next record

                    word_data = await get_word_by_id(record.user_id, record.word_id)
                    user_data = await get_user_by_id(record.user_id)

                    message_text = (
                        f"Repeat this *{escape_markdown(word_data.word)}*\n"
                        f"Translation ||{escape_markdown(word_data.translation)}||"
                    )

                    await bot.send_message(
                        chat_id=user_data.tg_id,
                        text=message_text,
                        parse_mode="MarkdownV2"
                    )

                    # Define stage-based repetition times
                    stage_intervals = {
                        1: datetime.timedelta(minutes=20),
                        2: datetime.timedelta(minutes=60),
                        3: datetime.timedelta(days=1),
                        4: datetime.timedelta(days=2),
                        5: datetime.timedelta(days=6)
                    }

                    next_stage = record.stage + 1
                    next_interval = stage_intervals.get(record.stage, None)

                    if next_interval:
                        await update_schedule_by_id(
                            record.id, record.user_id, record.word_id,
                            next_stage, time + next_interval
                        )
                except TelegramForbiddenError:
                    logging.warning(f"User {user_data.tg_id} has blocked the bot. Removing from DB.")
                    # Here you can remove the user from your database if needed
                except Exception as e:
                    logging.error(f"Unexpected error while processing user {user_data.tg_id}: {e}", exc_info=True)

    except Exception as e:
        logging.error(f"Critical error in async_task: {e}", exc_info=True)

    print("Async task completed.")

# Main scheduler function
async def scheduler_main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(async_task, 'interval', seconds=60)  # Runs every 60 seconds
    scheduler.start()

    print("Scheduler started. Running in background.")
    while True:
        await asyncio.sleep(3600)  # Keep the scheduler running
