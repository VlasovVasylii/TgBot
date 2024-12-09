import asyncio
from db import init_db, seed_test_data
from scheduler import setup_reminders
from shared import dp, bot
from handlers import register_handlers


async def main():
    """Основной метод запуска бота."""
    init_db()  # Инициализация базы данных
    seed_test_data()  # Добавляем тестовые данные
    setup_reminders()  # Настройка напоминаний
    register_handlers(dp)  # Регистрация обработчиков
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
