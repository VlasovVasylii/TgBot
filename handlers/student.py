from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import FeedbackState
from db import execute_query
from keyboards import generate_back_button, generate_feedback_keyboard, generate_tutor_keyboard, student_menu, main_menu
from utils import get_user_role
from handlers import send_or_edit_message
from .main import send_main_menu

router = Router()


@router.callback_query(F.data == "student_functions")
async def student_functions(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Для студентов'."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await send_or_edit_message(
            call,
            text="❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=main_menu,
            edit=False
        )
        return

    await send_or_edit_message(
        call,
        text="🎓 Функции для студентов:",
        reply_markup=student_menu,
        edit=True
    )


@router.callback_query(F.data == "feedback")
async def feedback_start(call: CallbackQuery, state: FSMContext):
    """Начало процесса оставления отзыва."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await send_or_edit_message(
            call,
            text="❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=main_menu,
            edit=False
        )
        return

    tutors = execute_query("""
        SELECT DISTINCT t.id, t.name
        FROM tutors t
        JOIN bookings b ON b.tutor_id = t.id
        WHERE b.student_contact = ? AND b.status = 'completed'
    """, (call.from_user.id,), fetchall=True)

    if tutors:
        response = "📝 Выберите ID репетитора для отзыва:\n\n"
        for tutor_id, name in tutors:
            response += f"{tutor_id}: {name}\n"
        await send_or_edit_message(
            call,
            text=response,
            reply_markup=generate_back_button(),
            edit=True
        )
        await state.set_state(FeedbackState.waiting_for_tutor_id)
    else:
        await send_or_edit_message(
            call,
            text="❌ У вас нет завершённых занятий с репетиторами.",
            reply_markup=generate_back_button(),
            edit=False
        )


@router.message(FeedbackState.waiting_for_tutor_id)
async def handle_feedback_tutor(message: Message, state: FSMContext):
    """Выбор репетитора для отзыва."""
    tutor_id = message.text.strip()
    tutor = execute_query("SELECT id, name FROM tutors WHERE id = ?", (tutor_id,), fetchone=True)

    if tutor:
        await state.update_data(tutor_id=tutor[0])
        await state.set_state(FeedbackState.waiting_for_rating)
        await message.reply("⭐ Укажите рейтинг (1-5):")
    else:
        await message.reply("❌ Репетитор не найден. Попробуйте ещё раз.")


@router.message(FeedbackState.waiting_for_rating)
async def handle_feedback_rating(message: Message, state: FSMContext):
    """Указание рейтинга."""
    try:
        rating = int(message.text)
        if 1 <= rating <= 5:
            await state.update_data(rating=rating)
            await state.set_state(FeedbackState.waiting_for_comment)
            await message.reply("✍️ Напишите комментарий:")
        else:
            await message.reply("❌ Рейтинг должен быть от 1 до 5.")
    except ValueError:
        await message.reply("❌ Введите числовое значение от 1 до 5.")


@router.message(FeedbackState.waiting_for_comment)
async def save_feedback(message: Message, state: FSMContext):
    """Сохранение отзыва."""
    comment = message.text.strip()
    data = await state.get_data()
    tutor_id = data["tutor_id"]
    rating = data["rating"]

    execute_query("""
    INSERT INTO feedback (tutor_id, student_name, student_contact, rating, comment)
    VALUES (?, ?, ?, ?, ?)
    """, (tutor_id, message.from_user.full_name, message.from_user.id, rating, comment))

    update_tutor_rating(tutor_id)

    await state.clear()
    await message.reply("✅ Спасибо за ваш отзыв!")
    await send_main_menu(message)


@router.callback_query(F.data == "view_feedback")
async def view_feedback(call: CallbackQuery):
    """Просмотр отзывов ученика."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await send_or_edit_message(
            call,
            text="❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=main_menu,
            edit=False
        )
        return

    feedbacks = execute_query("""
        SELECT f.id, t.name, f.rating, f.comment
        FROM feedback f
        JOIN tutors t ON f.tutor_id = t.id
        WHERE f.student_contact = ?
    """, (call.from_user.id,), fetchall=True)

    if feedbacks:
        response = "📝 Ваши отзывы:\n\n"
        for feedback_id, tutor_name, rating, comment in feedbacks:
            response += f"#{feedback_id}: {tutor_name}\n⭐ {rating}\nКомментарий: {comment}\n\n"
            await call.message.answer(response, reply_markup=generate_feedback_keyboard(feedback_id))
    else:
        await send_or_edit_message(
            call,
            text="❌ У вас пока нет отзывов.",
            reply_markup=generate_back_button(),
            edit=False
        )


@router.callback_query(F.data == "calendar")
async def calendar_handler(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Календарь занятий'."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await send_or_edit_message(
            call,
            text="❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=main_menu,
            edit=False
        )
        return

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
        await send_or_edit_message(
            call,
            text=response,
            reply_markup=generate_back_button(),
            edit=False
        )
    else:
        await send_or_edit_message(
            call,
            text="❌ У вас нет предстоящих занятий.",
            reply_markup=generate_back_button(),
            edit=False
        )


@router.callback_query(F.data == "find_tutor")
async def find_tutor_handler(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Найти репетитора'."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await send_or_edit_message(
            call,
            text="❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=main_menu,
            edit=False
        )
        return

    tutors = execute_query("SELECT id, name FROM tutors", fetchall=True)
    if tutors:
        await send_or_edit_message(
            call,
            text="🔍 Выберите репетитора, чтобы увидеть отзывы:",
            reply_markup=generate_tutor_keyboard(tutors),
            edit=False
        )
    else:
        await send_or_edit_message(
            call,
            text="❌ Репетиторы пока недоступны.",
            reply_markup=generate_back_button(),
            edit=False
        )


def update_tutor_rating(tutor_id):
    """Обновление рейтинга преподавателя."""
    execute_query("""
    UPDATE tutors
    SET rating = (SELECT AVG(rating) FROM feedback WHERE tutor_id = ?),
        feedback_count = (SELECT COUNT(*) FROM feedback WHERE tutor_id = ?)
    WHERE id = ?
    """, (tutor_id, tutor_id, tutor_id))


def register_handlers_student(dp):
    dp.include_router(router)
