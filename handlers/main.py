from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from keyboards import main_menu, student_menu, tutor_menu
from utils import get_user_role

router = Router()


@router.message(F.text.startswith("/start"))
async def start_handler(message: Message, state: FSMContext):
    """Приветственное сообщение."""
    await state.clear()
    await message.reply(
        "👥 Зарегистрироваться — кнопка для перехода к регистрации.\n"
        "ℹ️ Помощь — кнопка для вызова справочной информации.\n"
        "🎓 Для студентов — кнопка для вызова функций, доступных студентам.\n"
        "📚 Для преподавателей — кнопка для вызова функций преподавателей.\n"
        "🛠 Для администраторов — кнопка для перехода к функциям администратора.\n\n"
        "Для начала выберите действие из меню.",
        reply_markup=main_menu
    )


@router.message(F.text.startswith("/help"))
async def help_handler(message: Message):
    """Справка по командам."""
    help_text = (
        "🤖 EduHelperBot - ваш помощник в учебе.\n\n 👥 Зарегистрироваться — кнопка для перехода к регистрации."
        "👥 Зарегистрироваться — кнопка для перехода к регистрации.\n"
        "ℹ️ Помощь — кнопка для вызова справочной информации.\n"
        "🎓 Для студентов — кнопка для вызова функций, доступных студентам.\n"
        "📚 Для преподавателей — кнопка для вызова функций преподавателей.\n"
        "🛠 Для администраторов — кнопка для перехода к функциям администратора.\n\n"
        "❓ Если у вас возникли вопросы, напишите администратору."
    )
    await message.reply(help_text, reply_markup=main_menu)


@router.callback_query(F.data == "main_menu")
async def send_main_menu(message_or_call: Message | CallbackQuery):
    """Отправка главного меню."""
    user_role = get_user_role(message_or_call.from_user.id)
    if user_role == "student":
        menu = student_menu  # Меню для студентов
    elif user_role == "tutor":
        menu = tutor_menu  # Меню для преподавателей
    else:
        menu = main_menu  # Основное меню для всех
    if isinstance(message_or_call, Message):
        await message_or_call.answer("📚 Главное меню. Выберите действие:", reply_markup=menu)
    elif isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.edit_text("📚 Главное меню. Выберите действие:", reply_markup=menu)


@router.callback_query(F.data == "help")
async def help_handler(call: CallbackQuery):
    """Обработка кнопки 'Помощь'."""
    help_text = (
        "🤖 EduHelperBot - ваш помощник в учебе.\n\n 👥 Зарегистрироваться — кнопка для перехода к регистрации."
        "👥 Зарегистрироваться — кнопка для перехода к регистрации.\n"
        "ℹ️ Помощь — кнопка для вызова справочной информации.\n"
        "🎓 Для студентов — кнопка для вызова функций, доступных студентам.\n"
        "📚 Для преподавателей — кнопка для вызова функций преподавателей.\n"
        "🛠 Для администраторов — кнопка для перехода к функциям администратора.\n\n"
        "❓ Если у вас возникли вопросы, напишите администратору."
    )
    await call.message.edit_text(help_text, reply_markup=main_menu)


def register_handlers_main(dp):
    dp.include_router(router)
