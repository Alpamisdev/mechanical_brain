from app.database.models import User, Word, RepetitionSchedule, ActivityLog, SystemSetting, async_session
import datetime, logging
from sqlalchemy.sql import and_
import datetime


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


