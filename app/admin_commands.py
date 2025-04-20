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

admin_router = Router()

@admin_router.message(Command('stats'))
async def get_statistics(message: Message):
    """Handler for the /stats command - shows basic bot statistics"""
    # Check if user is an admin (you can add admin IDs to a list or env variable)
    admin_ids = [1672596043]  # Added the current user for testing
    
    if message.from_user.id not in admin_ids:
        await message.answer("You don't have permission to view statistics.")
        return
    
    await rq.log_command(message.from_user.id, "/stats")
    
    # Get statistics
    stats = await rq.get_comprehensive_statistics()
    
    # Format the message - using HTML instead of Markdown for better compatibility
    stats_message = (
        "<b>📊 Bot Statistics 📊</b>\n\n"
        "<b>👥 User Metrics</b>\n"
        f"• Total Users: {stats['total_users']}\n"
        f"• Daily Active Users: {stats['daily_active_users']}\n"
        f"• Weekly Active Users: {stats['weekly_active_users']}\n"
        f"• Monthly Active Users: {stats['monthly_active_users']}\n"
        f"• Retention Rate: {stats['retention_rate']:.2f}%\n\n"
        
        "<b>📚 Word Metrics</b>\n"
        f"• Total Words: {stats['total_words']}\n"
        f"• Words Added Today: {stats['words_added_today']}\n"
        f"• Words Added This Month: {stats['words_added_this_month']}\n"
        f"• Total Learned Words: {stats['total_learned_words']}\n"
        f"• Average Words Per User: {stats['avg_words_per_user']:.2f}\n\n"
        
        "<b>⏱ Engagement Metrics</b>\n"
        f"• Average Session Length: {stats['avg_session_minutes']:.2f} minutes\n"
    )
    
    # Add most popular commands if available
    if stats['popular_commands']:
        stats_message += "\n<b>📋 Most Popular Commands</b>\n"
        for cmd, count in stats['popular_commands']:
            stats_message += f"• {cmd}: {count} uses\n"
    
    # Add most active users if available
    if stats['most_active_users']:
        stats_message += "\n<b>🏆 Most Active Users</b>\n"
        for tg_id, name, count in stats['most_active_users']:
            # Escape HTML special characters in user names
            safe_name = name.replace('<', '&lt;').replace('>', '&gt;') if name else "Unknown"
            stats_message += f"• {safe_name}: {count} commands\n"
    
    # Split the message if it's too long
    message_parts = split_long_message(stats_message)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part, parse_mode="HTML")

@admin_router.message(Command('period_stats'))
async def get_period_statistics(message: Message):
    """Handler for the /detailed_stats command - shows detailed statistics with graphs"""
    # Check if user is an admin
    admin_ids = [1672596043]  # Added the current user for testing
    
    if message.from_user.id not in admin_ids:
        await message.answer("You don't have permission to view detailed statistics.")
        return
    
    await rq.log_command(message.from_user.id, "/detailed_stats")
    
    # Get statistics
    stats = await rq.get_comprehensive_statistics()
    
    # Format user growth data - using HTML instead of Markdown
    user_growth_message = "<b>👥 User Growth (Last 7 Days)</b>\n"
    for date, count in stats['user_growth']:
        user_growth_message += f"• {date.strftime('%Y-%m-%d')}: {count} new users\n"
    
    # Format word growth data
    word_growth_message = "<b>📚 Word Growth (Last 7 Days)</b>\n"
    for date, count in stats['word_growth']:
        word_growth_message += f"• {date.strftime('%Y-%m-%d')}: {count} new words\n"
    
    # Format hour activity data
    hour_activity_message = "<b>⏰ Activity by Hour of Day</b>\n"
    for hour, count in stats['hour_activity']:
        hour_activity_message += f"• {int(hour):02d}:00: {count} commands\n"
    
    # Combine all detailed stats
    detailed_stats_message = (
        "<b>📊 Detailed Bot Statistics 📊</b>\n\n" +
        user_growth_message + "\n" +
        word_growth_message + "\n" +
        hour_activity_message
    )
    
    # Split the message if it's too long
    message_parts = split_long_message(detailed_stats_message)
    
    # Send each part as a separate message
    for part in message_parts:
        await message.answer(part, parse_mode="HTML")


@admin_router.message(Command('visual_stats'))
async def get_visual_statistics(message: Message):
    """Handler for the /visual_stats command - generates and sends visual statistics"""
    # Check if user is an admin
    admin_ids = [1672596043]  # Replace with actual admin IDs
    
    if message.from_user.id not in admin_ids:
        await message.answer("You don't have permission to view visual statistics.")
        return
    
    await rq.log_command(message.from_user.id, "/visual_stats")
    await message.answer("Generating visual statistics... This may take a moment.")
    
    # Get statistics
    stats = await rq.get_comprehensive_statistics()
    
    # Generate charts
    user_growth_chart = await generate_user_growth_chart(stats['user_growth'])
    activity_heatmap = await generate_activity_heatmap(stats['hour_activity'])
    monthly_report = await generate_monthly_report(stats)
    
    # Send charts
    if user_growth_chart:
        await message.answer_photo(
            FSInputFile(user_growth_chart, filename="user_growth.png"),
            caption="User Growth Over Time (Last 7 Days)"
        )
    
    if activity_heatmap:
        await message.answer_photo(
            FSInputFile(activity_heatmap, filename="activity_heatmap.png"),
            caption="Activity by Hour of Day"
        )
    
    if monthly_report:
        await message.answer_photo(
            FSInputFile(monthly_report, filename="monthly_report.png"),
            caption="Monthly Statistics Report"
        )
    
    await message.answer("Visual statistics generated successfully.")

@admin_router.message(Command('export_stats'))
async def export_statistics(message: Message):
    """Handler for the /export_stats command - exports statistics as CSV"""
    # Check if user is an admin
    admin_ids = [1672596043]  # Replace with actual admin IDs
    
    if message.from_user.id not in admin_ids:
        await message.answer("You don't have permission to export statistics.")
        return
    
    await rq.log_command(message.from_user.id, "/export_stats")
    await message.answer("Generating statistics export... This may take a moment.")
    
    # Get statistics
    stats = await rq.get_comprehensive_statistics()
    
    # Create CSV content
    csv_content = "Metric,Value\n"
    csv_content += f"Total Users,{stats['total_users']}\n"
    csv_content += f"Daily Active Users,{stats['daily_active_users']}\n"
    csv_content += f"Weekly Active Users,{stats['weekly_active_users']}\n"
    csv_content += f"Monthly Active Users,{stats['monthly_active_users']}\n"
    csv_content += f"Total Words,{stats['total_words']}\n"
    csv_content += f"Words Added Today,{stats['words_added_today']}\n"
    csv_content += f"Words Added This Month,{stats['words_added_this_month']}\n"
    csv_content += f"Total Learned Words,{stats['total_learned_words']}\n"
    csv_content += f"Average Words Per User,{stats['avg_words_per_user']:.2f}\n"
    csv_content += f"Average Session Minutes,{stats['avg_session_minutes']:.2f}\n"
    csv_content += f"Retention Rate,{stats['retention_rate']:.2f}%\n"
    
    # Write to file
    with open("bot_statistics.csv", "w") as f:
        f.write(csv_content)
    
    # Send file
    await message.answer_document(
        FSInputFile("bot_statistics.csv", filename="bot_statistics.csv"),
        caption="Bot Statistics Export"
    )

# Add a function to update daily statistics
async def update_daily_stats():
    """Update daily statistics - to be called by scheduler"""
    await rq.update_daily_statistics()

# Add a function to track user sessions
async def track_user_sessions():
    """End inactive sessions - to be called by scheduler"""
    # Get all users with active sessions
    # End sessions for users who haven't been active for more than 30 minutes
    # This would require additional database functions
    pass

# Update the scheduler_main function to include these new tasks
async def scheduler_main():
    scheduler = AsyncIOScheduler()
    
    # Existing tasks
    scheduler.add_job(async_task, 'interval', seconds=60)
    
    # New tasks
    scheduler.add_job(update_daily_stats, 'cron', hour=0, minute=0)  # Run at midnight
    scheduler.add_job(track_user_sessions, 'interval', minutes=15)  # Check every 15 minutes
    
    scheduler.start()
    
    print("Scheduler started. Running in background.")
    while True:
        await asyncio.sleep(3600)  # Keep the scheduler running

# Add middleware to track all message handlers
@admin_router.message()
async def track_all_messages(message: Message, state: FSMContext):
    """Track all messages to update user activity"""
    await rq.update_user_activity(message.from_user.id)
    
    # If this is a command, log it
    if message.text and message.text.startswith('/'):
        await rq.log_command(message.from_user.id, message.text)
    
    # Continue processing with other handlers
    return None
