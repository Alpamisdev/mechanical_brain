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
from app.bot import bot

import aiogram.exceptions as exceptions
# from aiogram import exceptions
import logging

from aiogram.filters import Command, Filter
from aiogram.types import Message

ad_router = Router()

print("send_ad loaded")

semaphore = asyncio.Semaphore(5)

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in [1672596043]

class AdSend(StatesGroup):
    ad_message = State()

async def send_message_to_users_handler(user_id, text, attempt=0, max_attempt=5):
    if attempt >= max_attempt:
        logging.warning(f"Too many attepmts for user {user_id}")
        return False
    try:
        await bot.send_message(user_id, text)
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [id: {user_id}] blocked by user")
    except exceptions.TelegramBadRequest as e:
        logging.exception(f"We cant send to [id: {user_id}]: {e}")
    except exceptions.TelegramRetryAfter as e:
        logging.warning(f"Limit is reached. Wait {e.retry_after} sec")
        await asyncio.sleep(e.retry_after)
        return await send_message_to_users_handler(user_id, text, attempt +1) # rekrusic retry
    except exceptions.TelegramAPIError as e:
        logging.exception(f"We cant send to [id: {user_id}]: {e}")
    else:
        logging.info(f"Message sent to [id: {user_id}]")
        return True
    return False


async def send_message_to_users(text, users_list):
    results = []
    batch_size = 30
    async def throttled_send(user_id, text):
        async with semaphore:
                try:
                    return await send_message_to_users_handler(user_id, text)
                except Exception as e:
                    print(f"[Error] user {user_id}: {e}")
                    await asyncio.sleep(1)

    for i in range(0, len(users_list), batch_size):
        chunk = users_list[i:i+batch_size]
        tasks = [throttled_send(user.tg_id, text) for user in chunk]
        results.extend(await asyncio.gather(*tasks, return_exceptions=True))
        await asyncio.sleep(1)
    success_count = 0
    for result in results:
        if isinstance(result, Exception):
            logging.error(f"[Gather Exception] in {result}")
        elif result is True:
            success_count += 1
    return success_count

@ad_router.message(Command('sendad'), IsAdmin())
async def send_ad_command(message: Message, state: FSMContext):
    print("send_ad command loaded")
    await state.set_state(AdSend.ad_message)
    await message.answer('Send text of the ad.')

@ad_router.message(AdSend.ad_message, IsAdmin())
async def send_ad_to_users_command(message: Message, state: FSMContext):
    await state.update_data(ad_message=message.text)
    
    data = await state.get_data()
    text = data.get('ad_message')

    users_list = await rq.get_all_users()
    logging.info(f"Sending message to {len(users_list)} users.")

    count = await send_message_to_users(text, users_list)
    await message.answer(f'Ad sent to {count} users')
    await state.clear()

