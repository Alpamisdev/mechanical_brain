import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.requests import get_all_schedules

# Асинхронная задача
async def async_task():
    try:
        data = await get_all_schedules()
        if not data:
            print("Нет данных для обработки")
        else:
            for record in data:
                print(
                    f"ID: {record.id}, "
                    f"User ID: {record.user_id}, "
                    f"Word ID: {record.word_id}, "
                    f"Stage: {record.stage}, "
                    f"Next Review: {record.next_review_at}, "
                    f"Is Difficult: {record.is_difficult}, "
                    f"Attempts: {record.attempts}, "
                    f"Last Result: {record.last_result}"
                )
    except Exception as e:
        print(f"Ошибка в async_task: {e}")
    print("Асинхронная задача завершилась!")

# Основная функция
async def main():
    # Создание планировщика
    scheduler = AsyncIOScheduler()
    scheduler.add_job(async_task, 'interval', seconds=5)
    scheduler.start()

    print("Планировщик запущен. Основное приложение работает.")
    while True:
        await asyncio.sleep(1)  # Основной цикл приложения

# Запуск программы
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Программа завершена.")