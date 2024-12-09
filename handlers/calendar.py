from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from db import execute_query
from keyboards import generate_back_button

router = Router()


@router.callback_query(F.data == "calendar")
async def calendar_handler(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Календарь занятий'."""
    await state.clear()
    bookings = execute_query("""
    SELECT t.name, b.date, b.time, b.status
    FROM bookings b
    JOIN tutors t ON b.tutor_id = t.id
    WHERE b.student_contact = ?
    ORDER BY b.date, b.time
    """, (call.from_user.id,), fetchall=True)

    if bookings:
        response = "📅 Ваши предстоящие занятия:\n\n"
        for tutor_name, date, time, status in bookings:
            response += f"👩‍🏫 Репетитор: {tutor_name}\n📆 Дата: {date}, время: {time}\n📌 Статус: {status}\n\n"
    else:
        response = "❌ У вас нет предстоящих занятий."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


def register_handlers_calendar(dp):
    dp.include_router(router)
