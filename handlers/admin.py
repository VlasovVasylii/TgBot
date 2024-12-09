from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db import execute_query
from keyboards import generate_admin_panel_keyboard, generate_back_button
from config import ADMIN_CHAT_ID

router = Router()


@router.message(F.text.startswith("/admin"))
async def admin_panel(message: Message):
    """Панель администратора."""
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.reply("❌ У вас нет доступа к панели администратора.")
        return

    await message.reply("📋 Панель администратора:", reply_markup=generate_admin_panel_keyboard())


@router.callback_query(F.data == "manage_tutors")
async def manage_tutors(call: CallbackQuery):
    """Управление репетиторами."""
    tutors = execute_query("SELECT id, name, subject, rating FROM tutors", fetchall=True)

    if tutors:
        response = "👨‍🏫 Список репетиторов:\n\n"
        for tutor_id, name, subject, rating in tutors:
            response += f"ID: {tutor_id}\nИмя: {name}\nПредмет: {subject}\nРейтинг: {rating:.1f}\n\n"
        await call.message.edit_text(response, reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Репетиторы отсутствуют.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "manage_users")
async def manage_users(call: CallbackQuery):
    """Управление пользователями."""
    users = execute_query("SELECT id, full_name, role FROM users", fetchall=True)

    if users:
        response = "👥 Список пользователей:\n\n"
        for user_id, full_name, role in users:
            response += f"ID: {user_id}\nИмя: {full_name}\nРоль: {'Студент' if role == 'student' else 'Репетитор'}\n\n"
        await call.message.edit_text(response, reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Пользователи отсутствуют.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "manage_feedbacks")
async def manage_feedbacks(call: CallbackQuery):
    """Управление отзывами."""
    feedbacks = execute_query("""
    SELECT f.id, t.name, f.rating, f.comment, f.student_name
    FROM feedback f
    JOIN tutors t ON f.tutor_id = t.id
    """, fetchall=True)

    if feedbacks:
        response = "⭐ Список отзывов:\n\n"
        for feedback_id, tutor_name, rating, comment, student_name in feedbacks:
            response += (
                f"ID: {feedback_id}\n"
                f"Репетитор: {tutor_name}\nСтудент: {student_name}\n"
                f"Рейтинг: {rating}\nКомментарий: {comment}\n\n"
            )
        await call.message.edit_text(response, reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Отзывы отсутствуют.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "manage_bookings")
async def manage_bookings(call: CallbackQuery):
    """Управление занятиями."""
    bookings = execute_query("""
    SELECT b.id, t.name, b.student_name, b.date, b.time, b.status
    FROM bookings b
    JOIN tutors t ON b.tutor_id = t.id
    """, fetchall=True)

    if bookings:
        response = "📅 Список занятий:\n\n"
        for booking_id, tutor_name, student_name, date, time, status in bookings:
            response += (
                f"ID: {booking_id}\n"
                f"Репетитор: {tutor_name}\n"
                f"Студент: {student_name}\nДата: {date}, время: {time}\nСтатус: {status}\n\n"
            )
        await call.message.edit_text(response, reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Занятия отсутствуют.", reply_markup=generate_back_button())
    await call.answer()


def register_handlers_admin(dp):
    dp.include_router(router)
