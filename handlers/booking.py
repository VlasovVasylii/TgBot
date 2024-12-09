from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import BookingState
from datetime import datetime, timedelta
from db import execute_query
from keyboards import generate_back_button, generate_tutor_keyboard, generate_confirm_booking_keyboard
from aiogram import Router, F
from aiogram_calendar.simple_calendar import SimpleCalendar, SimpleCalendarCallback

router = Router()


@router.callback_query(F.data == "book")
async def start_booking(call: CallbackQuery, state: FSMContext):
    """Начало процесса бронирования."""
    await state.clear()
    tutors = execute_query("SELECT id, name FROM tutors", fetchall=True)
    if tutors:
        response = "📖 Выберите репетитора для бронирования:\n"
        for tutor_id, name in tutors:
            response += f"{tutor_id}: {name}\n"
        await call.message.edit_text(response, reply_markup=generate_tutor_keyboard(tutors))
        await state.set_state(BookingState.waiting_for_tutor_id)
    else:
        await call.message.edit_text("❌ Преподаватели пока недоступны.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(BookingState.waiting_for_tutor_id)
async def handle_tutor_selection(call: CallbackQuery, state: FSMContext):
    """Обработка выбора репетитора."""
    tutor_id = call.data.split("_")[1]
    tutor = execute_query("SELECT id, name FROM tutors WHERE id = ?", (tutor_id,), fetchone=True)
    if tutor:
        await state.update_data(tutor_id=tutor[0])
        await call.message.edit_text("📅 Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(BookingState.waiting_for_date)
    else:
        await call.message.edit_text("❌ Репетитор не найден. Попробуйте ещё раз.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(call: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """Обработка выбора даты."""
    result, key, step = await SimpleCalendar().process_selection(call, callback_data)
    if result:
        selected_date_str = result.strftime("%Y-%m-%d")
        if datetime.strptime(selected_date_str, "%Y-%m-%d").date() >= datetime.now().date():
            await state.update_data(date=selected_date_str)
            await call.message.edit_text(
                f"📅 Вы выбрали дату {selected_date_str}.\nТеперь укажите время (HH:MM):"
            )
            await state.set_state(BookingState.waiting_for_time)
        else:
            await call.message.edit_text(
                "❌ Нельзя выбрать прошедшую дату. Попробуйте снова.",
                reply_markup=await SimpleCalendar().start_calendar()
            )
    else:
        await call.message.edit_text("❌ Выбор даты отменён. Попробуйте снова.", reply_markup=generate_back_button())
    await call.answer()


@router.message(BookingState.waiting_for_time)
async def handle_booking_time(message: Message, state: FSMContext):
    """Обработка времени с проверкой."""
    time = message.text.strip()
    try:
        # Проверка формата времени
        datetime.strptime(time, "%H:%M")

        # Проверка времени бронирования
        data = await state.get_data()
        date = data["date"]
        selected_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        if selected_datetime <= datetime.now() + timedelta(hours=1.5):
            await message.reply("❌ Бронирование возможно не позже, чем за 1 час до начала занятия.")
            return

        await state.update_data(time=time)
        await state.set_state(BookingState.waiting_for_comment)
        await message.reply("💬 Добавьте комментарий для репетитора (или отправьте 'нет'):")
    except ValueError:
        await message.reply("❌ Неверный формат времени. Введите время в формате HH:MM.")


@router.message(BookingState.waiting_for_comment)
async def handle_booking_comment(message: Message, state: FSMContext):
    """Сохранение комментария и подтверждение бронирования."""
    comment = message.text.strip()
    comment = comment if comment.lower() != "нет" else ""
    await state.update_data(comment=comment)

    data = await state.get_data()
    tutor_id = data["tutor_id"]
    date = data["date"]
    time = data["time"]

    tutor = execute_query("SELECT name FROM tutors WHERE id = ?", (tutor_id,), fetchone=True)
    if tutor:
        tutor_name = tutor[0]
        await state.set_state(BookingState.confirm_booking)
        await message.reply(
            f"📅 Подтверждение бронирования:\n"
            f"Репетитор: {tutor_name}\nДата: {date}\nВремя: {time}\nКомментарий: {comment}\n\n"
            "✅ Подтвердите или отмените бронирование.",
            reply_markup=generate_confirm_booking_keyboard()
        )
    else:
        await message.reply("❌ Репетитор не найден.")


def register_handlers_booking(dp):
    dp.include_router(router)
