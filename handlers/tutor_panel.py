from aiogram import Router, F
from aiogram.types import CallbackQuery
from db import execute_query
from keyboards import generate_back_button

router = Router()


@router.callback_query(F.data == "tutor_panel")
async def tutor_panel(call: CallbackQuery):
    """Главное меню панели репетитора."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id, name FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if tutor:
        tutor_id, tutor_name = tutor
        response = f"📈 Панель репетитора {tutor_name}:\n\n"
        response += "- 🔍 Просмотр отзывов: выберите соответствующий фильтр\n"
        response += "- 📅 Предстоящие занятия: нажмите кнопку ниже\n"
        await call.message.edit_text(response, reply_markup=generate_tutor_panel_keyboard())
    else:
        await call.message.edit_text("❌ Вы не зарегистрированы как репетитор.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data.startswith("reviews_"))
async def filtered_reviews(call: CallbackQuery):
    """Фильтрация отзывов."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if tutor:
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
    else:
        response = "❌ Вы не зарегистрированы как репетитор."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "upcoming_classes")
async def upcoming_classes(call: CallbackQuery):
    """Просмотр предстоящих занятий репетитора."""
    tutor_contact = f"@{call.from_user.username}"
    tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor_contact,), fetchone=True)

    if tutor:
        tutor_id = tutor[0]
        upcoming_classes_ = execute_query("""
        SELECT student_name, date, time, comment FROM bookings
        WHERE tutor_id = ? AND status = 'pending'
        ORDER BY date, time
        """, (tutor_id,), fetchall=True)

        if upcoming_classes_:
            response = "📅 Предстоящие занятия:\n\n"
            for student_name, date, time, comment in upcoming_classes_:
                response += f"👩‍🎓 {student_name}: {date} в {time}\nКомментарий: {comment}\n\n"
        else:
            response = "❌ У вас нет предстоящих занятий."
    else:
        response = "❌ Вы не зарегистрированы как репетитор."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


def generate_tutor_panel_keyboard():
    """Клавиатура панели репетитора."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Высокий рейтинг", callback_data="reviews_high_rating"),
         InlineKeyboardButton(text="⭐ Низкий рейтинг", callback_data="reviews_low_rating")],
        [InlineKeyboardButton(text="📅 Предстоящие занятия", callback_data="upcoming_classes")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
    ])


def register_handlers_tutor_panel(dp):
    dp.include_router(router)
