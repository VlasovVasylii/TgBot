from aiogram import Router, F
from aiogram.types import CallbackQuery
from states import AdminState
from aiogram.fsm.context import FSMContext
from services import execute_query
from keyboards import admin_menu, generate_back_button, main_menu

router = Router()


@router.callback_query(F.data == "admin")
async def admin_panel(call: CallbackQuery):
    """
    Панель администратора. Проверяет права доступа по ID пользователя.
    """
    # Проверка на наличие пользователя в таблице администраторов
    admin = execute_query(
        "SELECT name FROM admins WHERE id = ?", (call.from_user.id,), fetchone=True
    )

    if not admin:
        await call.message.edit_text("❌ У вас нет доступа к панели администратора.",
                                     reply_markup=main_menu)
        await call.answer()
        return

    await call.message.edit_text(
        f"📋 Добро пожаловать в панель администратора, {admin[0]}:",
        reply_markup=admin_menu
    )
    await call.answer()


@router.callback_query(AdminState.waiting_for_manage_action, F.data.in_(
    ["manage_tutors", "manage_users", "manage_feedbacks", "manage_bookings"]))
async def manage_actions(call: CallbackQuery, state: FSMContext):
    """Обработка действий администратора."""
    action = call.data
    if action == "manage_tutors":
        await handle_manage_tutors(call)
    elif action == "manage_users":
        await handle_manage_users(call)
    elif action == "manage_feedbacks":
        await handle_manage_feedbacks(call)
    elif action == "manage_bookings":
        await handle_manage_bookings(call)
    else:
        await call.message.edit_text("❌ Неизвестное действие.", reply_markup=generate_back_button())
    await call.answer()


async def handle_manage_tutors(call: CallbackQuery):
    """Управление репетиторами."""
    tutors = execute_query("SELECT id, name, subject, rating FROM tutors", fetchall=True)

    if tutors:
        response = "👨‍🏫 Список репетиторов:\n\n"
        for tutor_id, name, subject, rating in tutors:
            response += f"ID: {tutor_id}\nИмя: {name}\nПредмет: {subject}\nРейтинг: {rating:.1f}\n\n"
        await call.message.edit_text(response, reply_markup=admin_menu)
    else:
        await call.message.edit_text("❌ Репетиторы отсутствуют.", reply_markup=generate_back_button())


async def handle_manage_users(call: CallbackQuery):
    """Управление пользователями."""
    students = execute_query("SELECT id, full_name, contact FROM students", fetchall=True)
    tutors = execute_query("SELECT id, name, subject, contact FROM tutors", fetchall=True)

    response = "👥 Список пользователей:\n\n"

    if students:
        response += "👨‍🎓 Студенты:\n"
        for student_id, full_name, contact in students:
            response += f"ID: {student_id}\nИмя: {full_name}\nКонтакт: {contact}\n\n"

    if tutors:
        response += "👨‍🏫 Преподаватели:\n"
        for tutor_id, name, subject, contact in tutors:
            response += f"ID: {tutor_id}\nИмя: {name}\nПредмет: {subject}\nКонтакт: {contact}\n\n"

    if not students and not tutors:
        response = "❌ Пользователи отсутствуют."

    await call.message.edit_text(response, reply_markup=admin_menu)


async def handle_manage_feedbacks(call: CallbackQuery):
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
        await call.message.edit_text(response, reply_markup=admin_menu)
    else:
        await call.message.edit_text("❌ Отзывы отсутствуют.", reply_markup=generate_back_button())


async def handle_manage_bookings(call: CallbackQuery):
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
        await call.message.edit_text(response, reply_markup=admin_menu)
    else:
        await call.message.edit_text("❌ Занятия отсутствуют.", reply_markup=generate_back_button())


def register_handlers_admin(dp):
    dp.include_router(router)
