from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import main_menu

router = Router()


@router.message(F.text.startswith("/start"))
async def start_handler(message: Message, state: FSMContext):
    """Приветственное сообщение."""
    await state.clear()
    await message.reply(
        "👋 Добро пожаловать в EduHelperBot!\n\n"
        "📚 Основные функции:\n"
        "1️⃣ Найти репетитора\n"
        "2️⃣ Календарь занятий\n"
        "3️⃣ Генерация тестов и помощь с задачами\n\n"
        "Для начала выберите действие из меню.",
        reply_markup=main_menu
    )


@router.message(F.text.startswith("/help"))
async def help_handler(message: Message):
    """Справка по командам."""
    help_text = (
        "🤖 EduHelperBot - ваш помощник в учебе.\n\n"
        "📚 Основные команды:\n"
        "/start - Запустить бота\n"
        "/generate_test <тема> - Сгенерировать учебный тест\n"
        "/solve_problem <задача> - Получить объяснение задачи\n"
        "/menu - Главное меню\n"
        "/help - Справка по командам\n\n"
        "❓ Если у вас возникли вопросы, напишите администратору."
    )
    await message.reply(help_text, reply_markup=main_menu)


def register_handlers_main(dp):
    dp.include_router(router)
