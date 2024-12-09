from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from keyboards import main_menu, student_menu, tutor_menu
from utils import get_user_role

router = Router()


@router.callback_query(F.data == "main_menu")
async def send_main_menu(message_or_call: Message | CallbackQuery, state: FSMContext):
    """Отправка главного меню."""
    user_role = get_user_role(message_or_call.from_user.id)
    if user_role == "student":
        menu = student_menu  # Меню для студентов
    elif user_role == "tutor":
        menu = tutor_menu  # Меню для преподавателей
    else:
        menu = main_menu  # Основное меню для всех
    await state.clear()
    if isinstance(message_or_call, Message):
        await message_or_call.answer("📚 Главное меню. Выберите действие:", reply_markup=menu)
    elif isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.edit_text("📚 Главное меню. Выберите действие:", reply_markup=menu)


@router.callback_query(F.data == "help")
async def help_handler(call: CallbackQuery):
    """Обработка кнопки 'Помощь'."""
    help_text = (
        "🤖 EduHelperBot - ваш помощник в учебе.\n\n"
        "📚 Основные функции:\n"
        "- 🔍 Найти репетитора\n"
        "- 📅 Календарь занятий\n"
        "- 📝 Генерация тестов: команда /generate_test\n"
        "- 🤔 Объяснение задач: команда /solve_problem\n"
        "ℹ️ Если у вас возникли вопросы, напишите администратору."
    )
    await call.message.edit_text(help_text, reply_markup=main_menu)


def register_handlers_menu(dp):
    dp.include_router(router)
