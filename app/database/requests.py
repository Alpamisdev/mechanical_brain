from app.database.models import User, Word, RepetitionSchedule, ActivityLog, SystemSetting, async_session
import datetime, logging
from sqlalchemy.sql import and_
import datetime

import datetime
from sqlalchemy import select, and_, func, desc, extract
from app.database.models import User, Word, RepetitionSchedule, CommandLog, UserSession, DailyStatistic, async_session


from sqlalchemy import select, update, delete

async def get_current_time():
    return datetime.datetime.now()

async def get_user_by_id(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))
        return user

async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user

async def get_all_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users.all()

async def set_user(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()


async def get_word_by_id(user_id, word_id):
    async with async_session() as session:
        word_obj = await session.scalar(select(Word).where(and_(Word.id == word_id, Word.user_id == user_id)))
        if word_obj:
            return word_obj
        else:
            logging.warning(f"Word with ID {word_id} for user {user_id} not found.")
            return None

async def set_word(user_id, word, translation):
    async with async_session() as session:
        # word_obj = await session.scalar(select(Word).where(Word.user_id == user_id and Word.word == word))
        word_obj = await session.scalar(select(Word).where(and_(Word.word == word, Word.user_id == user_id)))

        if not word_obj:
            new_word = Word(user_id=user_id, word=word, translation=translation)
            session.add(new_word)
            await session.commit()
            return True
        else:
            return False

async def get_word(user_id, word):
    async with async_session() as session:
        word_obj = await session.scalar(select(Word).where(and_(Word.word == word, Word.user_id == user_id)))
        if word_obj:
            return word_obj.id
        else:
            logging.warning(f"Word with {word} for user {user_id} not found.")
            return None

async def get_words_by_user(tg_id):
    async with async_session() as session:
        # print('___________________________' , tg_id)
        user_id = await get_user(tg_id)
        words = await session.scalars(select(Word).where(Word.user_id == user_id.id))
        return words.all()

async def set_schedule(user_id, word_id, stage, next_review_at, is_difficult=False, attempts=0, last_result=None):
    async with async_session() as session:
        schedule = RepetitionSchedule(
            user_id=user_id,
            word_id=word_id,
            stage=stage,
            next_review_at=next_review_at,
            is_difficult=is_difficult,
            attempts=attempts,
            last_result=last_result
        )
        session.add(schedule)
        await session.commit()

async def get_all_schedules_now():
    async with async_session() as session:
        time = await get_current_time()
        schedules = await session.scalars(select(RepetitionSchedule).where(RepetitionSchedule.next_review_at <= time))
        return schedules.all()

async def update_schedule_by_id(id, user_id, word_id, stage, next_review_at):
    async with async_session() as session:
        # Retrieve the schedule by its ID
        schedule = await session.scalar(
            select(RepetitionSchedule).where(RepetitionSchedule.id == id)
        )
        
        if schedule:
            # Update the schedule's stage and next repetition time
            schedule.stage = stage
            schedule.next_review_at = next_review_at
            await session.commit()
        else:
            print(f"Schedule with ID {id} not found.")


# code of v0
async def get_learned_words(user_id):
    """Get words with stage >= 7 (considered learned)"""
    async with async_session() as session:
        # First get all schedules with stage >= 7
        schedules = await session.scalars(
            select(RepetitionSchedule)
            .where(and_(
                RepetitionSchedule.user_id == user_id,
                RepetitionSchedule.stage >= 7
            ))
        )
        
        learned_schedules = schedules.all()
        
        if not learned_schedules:
            return []
            
        # Get the word IDs from the schedules
        word_ids = [schedule.word_id for schedule in learned_schedules]
        
        # Get the actual words
        words = await session.scalars(
            select(Word)
            .where(Word.id.in_(word_ids))
        )
        
        return words.all()

async def get_words_added_this_month(user_id):
    """Get words added in the current month"""
    async with async_session() as session:
        # Get the current date and first day of the month
        now = datetime.datetime.now()
        first_day = datetime.datetime(now.year, now.month, 1)
        
        # Query words created this month
        words = await session.scalars(
            select(Word)
            .where(and_(
                Word.user_id == user_id,
                Word.created_at >= first_day,
                Word.created_at <= now
            ))
        )
        
        return words.all()

async def get_learned_words(user_id):
    """Get words with stage >= 7 (considered learned)"""
    async with async_session() as session:
        # First get all schedules with stage >= 7
        schedules = await session.scalars(
            select(RepetitionSchedule)
            .where(and_(
                RepetitionSchedule.user_id == user_id,
                RepetitionSchedule.stage >= 7
            ))
        )
        
        learned_schedules = schedules.all()
        
        if not learned_schedules:
            return []
            
        # Get the word IDs from the schedules
        word_ids = [schedule.word_id for schedule in learned_schedules]
        
        # Get the actual words
        words = await session.scalars(
            select(Word)
            .where(Word.id.in_(word_ids))
        )
        
        return words.all()

async def get_words_added_this_month(user_id):
    """Get words added in the current month"""
    async with async_session() as session:
        # Get the current date and first day of the month
        now = datetime.datetime.now()
        first_day = datetime.datetime(now.year, now.month, 1)
        
        # Query words created this month
        words = await session.scalars(
            select(Word)
            .where(and_(
                Word.user_id == user_id,
                Word.created_at >= first_day,
                Word.created_at <= now
            ))
        )
        
        return words.all()

async def get_period_statistics(days=7):
    """Get statistics for a specific time period"""
    async with async_session() as session:
        period_start = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # Get users who joined in this period
        new_users_result = await session.execute(
            select(func.count()).select_from(User).where(
                User.created_at >= period_start
            )
        )
        new_users = new_users_result.scalar() or 0
        
        # Get words added in this period
        new_words_result = await session.execute(
            select(func.count()).select_from(Word).where(
                Word.created_at >= period_start
            )
        )
        new_words = new_words_result.scalar() or 0
        
        # Get words that became learned (reached stage 6) in this period
        # This is more complex and might require additional tracking
        
        return {
            "period_days": days,
            "new_users": new_users,
            "new_words": new_words
        }

async def update_user_activity(tg_id):
    """Update user's last_active timestamp"""
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            user.last_active = datetime.datetime.now()
            await session.commit()
            return True
        return False

async def log_command(tg_id, command):
    """Log a command execution"""
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            command_log = CommandLog(
                user_id=user.id,
                command=command
            )
            session.add(command_log)
            await session.commit()
            return True
        return False

async def start_user_session(tg_id):
    """Start a new user session"""
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            # Check if there's an active session
            active_session = await session.scalar(
                select(UserSession)
                .where(and_(
                    UserSession.user_id == user.id,
                    UserSession.session_end.is_(None)
                ))
            )
            
            # If no active session, create one
            if not active_session:
                new_session = UserSession(
                    user_id=user.id
                )
                session.add(new_session)
                await session.commit()
                return True
        return False

async def end_user_session(tg_id):
    """End a user session and calculate duration"""
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            # Find active session
            active_session = await session.scalar(
                select(UserSession)
                .where(and_(
                    UserSession.user_id == user.id,
                    UserSession.session_end.is_(None)
                ))
            )
            
            if active_session:
                now = datetime.datetime.now()
                active_session.session_end = now
                # Calculate duration in seconds
                duration = (now - active_session.session_start).total_seconds()
                active_session.duration_seconds = int(duration)
                await session.commit()
                return True
        return False

async def update_daily_statistics():
    """Update or create daily statistics record"""
    async with async_session() as session:
        today = datetime.datetime.now().date()
        today_start = datetime.datetime.combine(today, datetime.time.min)
        today_end = datetime.datetime.combine(today, datetime.time.max)
        
        # Check if we already have a record for today
        daily_stat = await session.scalar(
            select(DailyStatistic)
            .where(
                func.date(DailyStatistic.date) == today
            )
        )
        
        if not daily_stat:
            # Create new record
            daily_stat = DailyStatistic(
                date=today_start
            )
            session.add(daily_stat)
        
        # Count active users today
        active_users_result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.last_active.between(today_start, today_end)
            )
        )
        daily_stat.active_users = active_users_result.scalar() or 0
        
        # Count new users today
        new_users_result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.created_at.between(today_start, today_end)
            )
        )
        daily_stat.new_users = new_users_result.scalar() or 0
        
        # Count words added today
        words_added_result = await session.execute(
            select(func.count())
            .select_from(Word)
            .where(
                Word.created_at.between(today_start, today_end)
            )
        )
        daily_stat.words_added = words_added_result.scalar() or 0
        
        # Count commands executed today
        commands_result = await session.execute(
            select(func.count())
            .select_from(CommandLog)
            .where(
                CommandLog.executed_at.between(today_start, today_end)
            )
        )
        daily_stat.total_commands = commands_result.scalar() or 0
        
        # Count words that reached stage 6 (learned) today
        # This is an approximation as we don't track exactly when a word reaches stage 6
        learned_words_result = await session.execute(
            select(func.count())
            .select_from(RepetitionSchedule)
            .where(and_(
                RepetitionSchedule.stage >= 7,
                RepetitionSchedule.next_review_at.between(today_start, today_end)
            ))
        )
        daily_stat.words_learned = learned_words_result.scalar() or 0
        
        await session.commit()
        return daily_stat

async def get_comprehensive_statistics():
    """Get comprehensive statistics about the bot"""
    async with async_session() as session:
        today = datetime.datetime.now().date()
        today_start = datetime.datetime.combine(today, datetime.time.min)
        today_end = datetime.datetime.combine(today, datetime.time.max)
        
        # Current month range
        month_start = datetime.datetime(today.year, today.month, 1)
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        month_end = next_month - datetime.timedelta(days=next_month.day)
        month_end = datetime.datetime.combine(month_end, datetime.time.max)
        
        # Total users
        total_users_result = await session.execute(select(func.count()).select_from(User))
        total_users = total_users_result.scalar() or 0
        
        # Daily active users
        daily_users_result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.last_active.between(today_start, today_end)
            )
        )
        daily_users = daily_users_result.scalar() or 0
        
        # Weekly active users
        week_ago = today - datetime.timedelta(days=7)
        week_start = datetime.datetime.combine(week_ago, datetime.time.min)
        weekly_users_result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.last_active.between(week_start, today_end)
            )
        )
        weekly_users = weekly_users_result.scalar() or 0
        
        # Monthly active users
        monthly_users_result = await session.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.last_active.between(month_start, month_end)
            )
        )
        monthly_users = monthly_users_result.scalar() or 0
        
        # Total words
        total_words_result = await session.execute(select(func.count()).select_from(Word))
        total_words = total_words_result.scalar() or 0
        
        # Words added today
        words_today_result = await session.execute(
            select(func.count())
            .select_from(Word)
            .where(
                Word.created_at.between(today_start, today_end)
            )
        )
        words_today = words_today_result.scalar() or 0
        
        # Words added this month
        words_month_result = await session.execute(
            select(func.count())
            .select_from(Word)
            .where(
                Word.created_at.between(month_start, month_end)
            )
        )
        words_month = words_month_result.scalar() or 0
        
        # Total learned words (stage >= 7)
        learned_words_result = await session.execute(
            select(func.count())
            .select_from(RepetitionSchedule)
            .where(
                RepetitionSchedule.stage >= 7
            )
        )
        learned_words = learned_words_result.scalar() or 0
        
        # Average words per user
        avg_words_per_user = total_words / total_users if total_users > 0 else 0
        
        # Most active users (top 5)
        most_active_users_result = await session.execute(
            select(User.tg_id, User.name, func.count(CommandLog.id).label('command_count'))
            .join(CommandLog, User.id == CommandLog.user_id)
            .group_by(User.id)
            .order_by(desc('command_count'))
            .limit(5)
        )
        most_active_users = most_active_users_result.fetchall()
        
        # Most popular commands (top 5)
        popular_commands_result = await session.execute(
            select(CommandLog.command, func.count().label('count'))
            .group_by(CommandLog.command)
            .order_by(desc('count'))
            .limit(5)
        )
        popular_commands = popular_commands_result.fetchall()
        
        # Average session duration (in minutes)
        avg_session_result = await session.execute(
            select(func.avg(UserSession.duration_seconds))
            .where(
                UserSession.duration_seconds.is_not(None)
            )
        )
        avg_session_seconds = avg_session_result.scalar() or 0
        avg_session_minutes = round(avg_session_seconds / 60, 2)
        
        # User retention (users active in the last 7 days / total users)
        retention_rate = (weekly_users / total_users * 100) if total_users > 0 else 0
        
        # User growth over time (last 7 days)
        user_growth_result = await session.execute(
            select(
                func.date(User.created_at).label('date'),
                func.count().label('count')
            )
            .where(
                User.created_at >= week_start
            )
            .group_by('date')
            .order_by('date')
        )
        user_growth = user_growth_result.fetchall()
        
        # Word growth over time (last 7 days)
        word_growth_result = await session.execute(
            select(
                func.date(Word.created_at).label('date'),
                func.count().label('count')
            )
            .where(
                Word.created_at >= week_start
            )
            .group_by('date')
            .order_by('date')
        )
        word_growth = word_growth_result.fetchall()
        
        # Activity by hour of day
        hour_activity_result = await session.execute(
            select(
                extract('hour', CommandLog.executed_at).label('hour'),
                func.count().label('count')
            )
            .group_by('hour')
            .order_by('hour')
        )
        hour_activity = hour_activity_result.fetchall()
        
        return {
            # Core metrics
            "total_users": total_users,
            "daily_active_users": daily_users,
            "weekly_active_users": weekly_users,
            "monthly_active_users": monthly_users,
            "total_words": total_words,
            "words_added_today": words_today,
            "words_added_this_month": words_month,
            "total_learned_words": learned_words,
            
            # Advanced metrics
            "avg_words_per_user": avg_words_per_user,
            "most_active_users": most_active_users,
            "popular_commands": popular_commands,
            "avg_session_minutes": avg_session_minutes,
            "retention_rate": retention_rate,
            "user_growth": user_growth,
            "word_growth": word_growth,
            "hour_activity": hour_activity
        }
