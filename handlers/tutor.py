from aiogram import Router, F
from aiogram.types import CallbackQuery
from db import execute_query
from keyboards import generate_filter_reviews_keyboard, main_menu, generate_back_button
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(F.data == "tutor_panel")
async def tutor_panel(call: CallbackQuery, state: FSMContext):
    """Панель репетитора."""
    await state.clear()
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id, name FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if tutor:
        tutor_id, tutor_name = tutor
        response = f"📈 Панель репетитора {tutor_name}:\n\n"
        response += "- 🔍 Просмотр отзывов: выберите фильтр ниже\n"
        response += "- 📅 Предстоящие занятия: нажмите на соответствующую кнопку\n"
        await call.message.edit_text(response, reply_markup=generate_filter_reviews_keyboard())
    else:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=main_menu)
    await call.answer()


@router.callback_query(F.data.startswith("filter_reviews_"))
async def filter_reviews(call: CallbackQuery):
    """Фильтрация отзывов по времени."""
    filter_type = call.data.split("_")[2]
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if not tutor:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=generate_back_button())
        return

    tutor_id = tutor[0]
    if filter_type == "month":
        query = """
            SELECT student_name, rating, comment, date('now') as created_at
            FROM feedback
            WHERE tutor_id = ? AND created_at >= date('now', '-1 month')
        """
    elif filter_type == "year":
        query = """
            SELECT student_name, rating, comment, date('now') as created_at
            FROM feedback
            WHERE tutor_id = ? AND created_at >= date('now', '-1 year')
        """
    else:
        query = """
            SELECT student_name, rating, comment, date('now') as created_at
            FROM feedback
            WHERE tutor_id = ?
        """

    feedbacks = execute_query(query, (tutor_id,), fetchall=True)

    if feedbacks:
        response = "📋 Ваши отзывы:\n\n"
        for student_name, rating, comment, created_at in feedbacks:
            response += f"👤 {student_name} ({created_at})\n⭐ {rating}\n💬 {comment}\n\n"
    else:
        response = "❌ Отзывы не найдены для выбранного периода."

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
    upcoming_classes = execute_query("""
        SELECT student_name, date, time, comment
        FROM bookings
        WHERE tutor_id = ? AND status IN ('pending', 'approved')
        ORDER BY date, time
    """, (tutor_id,), fetchall=True)

    if upcoming_classes:
        response = "📅 Ваши предстоящие занятия:\n\n"
        for student_name, date, time, comment in upcoming_classes:
            response += f"👩‍🎓 {student_name}: {date} в {time}\n💬 {comment}\n\n"
    else:
        response = "❌ У вас нет предстоящих занятий."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "tutor_analytics")
async def tutor_analytics(call: CallbackQuery):
    """Аналитика для репетиторов."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id, name FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if not tutor:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=generate_back_button())
        return

    tutor_id, tutor_name = tutor
    stats = execute_query("""
        SELECT COUNT(b.id), AVG(f.rating)
        FROM bookings b
        LEFT JOIN feedback f ON b.id = f.tutor_id
        WHERE b.tutor_id = ?
    """, (tutor_id,), fetchone=True)

    total_classes = stats[0] if stats[0] else 0
    avg_rating = f"{stats[1]:.2f}" if stats[1] else "Нет отзывов"

    response = (
        f"📊 Аналитика для репетитора {tutor_name}:\n\n"
        f"👥 Всего занятий: {total_classes}\n"
        f"⭐ Средний рейтинг: {avg_rating}"
    )

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


def register_handlers_tutor(dp):
    dp.include_router(router)
