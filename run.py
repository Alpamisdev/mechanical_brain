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

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    await async_main()
    
    # Set up the Dispatcher and include routers
    dp = Dispatcher()
    dp.include_router(user_router)
    
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
