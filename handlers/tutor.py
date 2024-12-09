from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from states import TestGenerationState
from db import execute_query
from keyboards import generate_back_button, generate_filter_reviews_keyboard, tutor_menu
from aiogram.fsm.context import FSMContext
from features import generate_test
from .main import send_main_menu
from utils import get_user_role

router = Router()


@router.callback_query(F.data == "tutor_functions")
async def tutor_panel(call: CallbackQuery):
    """Панель репетитора."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "tutor":
        await call.message.edit_text("❌ Доступ запрещён. Эта функция доступна только для преподавателей.",
                                     reply_markup=generate_back_button())
        await call.answer()
        return

    await call.message.edit_text(
        "📚 Функции для преподавателей:",
        reply_markup=tutor_menu
    )
    await call.answer()


@router.callback_query(F.data.startswith("reviews_"))
async def filtered_reviews(call: CallbackQuery):
    """Фильтрация отзывов."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if not tutor:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=generate_back_button())
        return

    tutor_id = tutor[0]
    filter_type = call.data.split("_")[1]
    query = "SELECT student_name, rating, comment FROM feedback WHERE tutor_id = ?"
    params = [tutor_id]

    if filter_type == "high_rating":
        query += " AND rating >= 4"
    elif filter_type == "low_rating":
        query += " AND rating <= 3"

    feedbacks = execute_query(query, params, fetchall=True)
    if feedbacks:
        response = "📊 Ваши отзывы:\n\n"
        for student_name, rating, comment in feedbacks:
            response += f"⭐ {rating} от {student_name}: {comment}\n"
    else:
        response = "❌ Отзывы по выбранному фильтру отсутствуют."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "upcoming_classes")
async def view_upcoming_classes(call: CallbackQuery):
    """Просмотр предстоящих занятий репетитора."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if not tutor:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=generate_back_button())
        return

    tutor_id = tutor[0]
    upcoming_classes_ = execute_query("""
        SELECT student_name, date, time, comment
        FROM bookings
        WHERE tutor_id = ? AND status IN ('pending', 'approved')
        ORDER BY date, time
    """, (tutor_id,), fetchall=True)

    if upcoming_classes_:
        response = "📅 Ваши предстоящие занятия:\n\n"
        for student_name, date, time, comment in upcoming_classes_:
            response += f"👩‍🎓 {student_name}: {date} в {time}\n💬 {comment}\n\n"
    else:
        response = "❌ У вас нет предстоящих занятий."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data.startswith("filter_reviews_"))
async def filter_reviews(call: CallbackQuery):
    """Фильтрация отзывов."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if not tutor:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=generate_back_button())
        return

    tutor_id = tutor[0]
    filter_type = call.data.split("_")[2]  # Получение типа фильтра

    # Формирование SQL-запроса в зависимости от типа фильтра
    if filter_type == "high_rating":
        query = """
            SELECT student_name, rating, comment
            FROM feedback
            WHERE tutor_id = ? AND rating >= 4
        """
    elif filter_type == "low_rating":
        query = """
            SELECT student_name, rating, comment
            FROM feedback
            WHERE tutor_id = ? AND rating <= 3
        """
    else:
        query = """
            SELECT student_name, rating, comment
            FROM feedback
            WHERE tutor_id = ?
        """

    feedbacks = execute_query(query, (tutor_id,), fetchall=True)

    if feedbacks:
        response = "📊 Ваши отзывы:\n\n"
        for student_name, rating, comment in feedbacks:
            response += f"👤 {student_name}\n⭐ {rating}\n💬 {comment}\n\n"
    else:
        response = "❌ Отзывы по выбранному фильтру отсутствуют."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "tutor_analytics")
async def tutor_analytics(call: CallbackQuery):
    """Аналитика для преподавателя."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id, name FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if not tutor:
        await call.message.edit_text("❌ Вы не зарегистрированы как преподаватель.", reply_markup=generate_back_button())
        return

    tutor_id, tutor_name = tutor

    # SQL-запрос для подсчёта занятий и среднего рейтинга
    stats = execute_query("""
        SELECT COUNT(b.id) AS total_classes, COALESCE(AVG(f.rating), 0) AS avg_rating
        FROM bookings b
        LEFT JOIN feedback f ON b.id = f.tutor_id
        WHERE b.tutor_id = ? AND b.status IN ('pending', 'approved', 'completed')
    """, (tutor_id,), fetchone=True)

    total_classes = stats[0]
    avg_rating = f"{stats[1]:.2f}" if stats[1] > 0 else "Нет отзывов"

    response = (
        f"📊 Аналитика для преподавателя {tutor_name}:\n\n"
        f"👥 Проведённых занятий: {total_classes}\n"
        f"⭐ Средний рейтинг: {avg_rating}"
    )

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "generate_test")
async def generate_test_start(call: CallbackQuery, state: FSMContext):
    """Начало процесса генерации теста."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "tutor":
        await call.message.edit_text("❌ Доступ запрещён. Эта функция доступна только для студентов.")
        await call.answer()
        return

    await state.clear()
    await state.set_state(TestGenerationState.waiting_for_topic)
    await call.message.edit_text("📚 Укажите тему теста:", reply_markup=generate_back_button())
    await call.answer()


@router.message(TestGenerationState.waiting_for_topic)
async def generate_test_for_topic(message: Message, state: FSMContext):
    """Генерация теста по теме."""
    topic = message.text
    await message.reply("⏳ Создаётся тест, пожалуйста, подождите...")
    try:
        test = generate_test(topic)
        await state.clear()
        await message.reply(f"✅ Тест по теме '{topic}':\n\n{test}")
    except Exception as e:
        await state.clear()
        await message.reply(f"❌ Ошибка генерации теста: {e}")
    await send_main_menu(message, state)


def register_handlers_tutor(dp):
    dp.include_router(router)
