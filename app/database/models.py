import os
from dotenv import load_dotenv
import datetime, string

from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

load_dotenv()

engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'), echo=False)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=True) # optional qiliw kerek
    created_at = mapped_column(DateTime, default=datetime.datetime.now())

class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    word: Mapped[str] = mapped_column(String)
    translation: Mapped[str] = mapped_column(String)
    created_at = mapped_column(DateTime, default=datetime.datetime.now) # meninmshe qaysi waqitta yagniy saattda qosilganin saqlaw kerek

    def __init__(self, user_id, word, translation):
        self.user_id = user_id
        self.word = word
        self.translation = translation

class RepetitionSchedule(Base):
    __tablename__ = 'repetation_schedulls'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'))
    stage: Mapped[int] = mapped_column(Integer)
    next_review_at = mapped_column(DateTime) # ChatGPT dan soraw kerek # usi jerde ne boliwin Turdibekten soraw kerek | bul jerge waqitta ham saatti qoyiw kerek boladi. Belgilengen waqitti
    is_difficult: Mapped[bool] = mapped_column(Boolean, default=False) # True yamasa False saqlaw kerek. Defult False boliw kerek
    attempts: Mapped[int] = mapped_column(Integer)
    last_result: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # def __repr__(self):
    #     return f"{self.word_id}, {self.user_id}"

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    attempted_at = mapped_column(DateTime, default=datetime.datetime.now) # bul jerge hazir qaytalagan waqti jaziladi.

class SystemSetting(Base):
    __tablename__ = 'system_settings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stage: Mapped[int] = mapped_column(Integer)
    interval_minutes: Mapped[int] = mapped_column(Integer)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
