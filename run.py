import os
import asyncio
import logging
from aiogram.methods.delete_webhook import DeleteWebhook

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from app.handlers import router as user_router
from app.scheduler import scheduler_main
from app.bot import bot
from app.database.models import async_main

from aiogram.exceptions import TelegramForbiddenError
from aiogram.types.error_event import ErrorEvent
from aiogram.filters.exception import ExceptionTypeFilter

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    await async_main()
    
    # Set up the Dispatcher and include routers
    dp = Dispatcher()
    dp.include_router(user_router)
    
    @dp.error(ExceptionTypeFilter(TelegramForbiddenError))
    async def handle_forbidden_error(event: ErrorEvent):
        print(f"User {event.update.message.chat.id} has blocked the bot.")
        # Remove user from database or log the issue

    @dp.error()
    async def global_error_handler(event: ErrorEvent):
        print(f"Critical error: {event.exception}")

    # Start the scheduler in the same event loop
    asyncio.create_task(scheduler_main())  # Run the scheduler as a background task

    # Start polling the bot
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())  # Start the main event loop
    except KeyboardInterrupt:
        print('Exit')
