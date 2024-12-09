from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from db import execute_query
from states import FeedbackState
from .menu import send_main_menu
from keyboards import generate_back_button, generate_feedback_keyboard

router = Router()


@router.callback_query(F.data == "feedback")
async def feedback_start(call: CallbackQuery, state: FSMContext):
    """Начало процесса оставления отзыва."""
    await state.clear()
    tutors = execute_query("""
        SELECT DISTINCT t.id, t.name
        FROM tutors t
        JOIN bookings b ON b.tutor_id = t.id
        WHERE b.student_contact = ? AND b.status = 'completed'
    """, (call.from_user.id,), fetchall=True)

    if tutors:
        response = "📝 Выберите ID репетитора для отзыва (вы занимались с ними):\n\n"
        for tutor_id, name in tutors:
            response += f"{tutor_id}: {name}\n"
        await call.message.edit_text(response, reply_markup=generate_back_button())
        await state.set_state(FeedbackState.waiting_for_tutor_id)
    else:
        await call.message.edit_text("❌ У вас нет завершённых занятий с репетиторами.",
                                     reply_markup=generate_back_button())
    await call.answer()


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

    # Сохранение отзыва
    execute_query("""
    INSERT INTO feedback (tutor_id, student_name, student_contact, rating, comment)
    VALUES (?, ?, ?, ?, ?)
    """, (tutor_id, message.from_user.full_name, message.from_user.id, rating, comment))

    # Обновление рейтинга преподавателя
    update_tutor_rating(tutor_id)

    await state.clear()
    await message.reply("✅ Спасибо за ваш отзыв!")
    await send_main_menu(message)


@router.callback_query(F.data == "view_feedback")
async def view_feedback(call: CallbackQuery):
    """Просмотр отзывов ученика."""
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
            # Отправляем клавиатуру для изменения/удаления
            await call.message.answer(response, reply_markup=generate_feedback_keyboard(feedback_id))
    else:
        await call.message.edit_text("❌ У вас пока нет отзывов.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data.startswith("edit_feedback_"))
async def edit_feedback(call: CallbackQuery, state: FSMContext):
    """Редактирование отзыва через клавиатуру."""
    feedback_id = call.data.split("_")[2]
    feedback = execute_query("""
        SELECT id, tutor_id, comment
        FROM feedback
        WHERE id = ? AND student_contact = ?
    """, (feedback_id, call.from_user.id), fetchone=True)

    if feedback:
        await state.update_data(feedback_id=feedback[0], tutor_id=feedback[1])
        await state.set_state(FeedbackState.waiting_for_rating)
        await call.message.edit_text("⭐ Укажите новый рейтинг (1-5):", reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Отзыв не найден или у вас нет прав на его изменение.",
                                     reply_markup=generate_back_button())


@router.callback_query(F.data.startswith("delete_feedback_"))
async def delete_feedback(call: CallbackQuery):
    """Удаление отзыва через клавиатуру."""
    feedback_id = call.data.split("_")[2]
    feedback = execute_query("""
        SELECT id, tutor_id
        FROM feedback
        WHERE id = ? AND student_contact = ?
    """, (feedback_id, call.from_user.id), fetchone=True)

    if feedback:
        tutor_id = feedback[1]
        execute_query("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        update_tutor_rating(tutor_id)
        await call.message.edit_text("✅ Отзыв удалён.", reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Отзыв не найден или у вас нет прав на его удаление.",
                                     reply_markup=generate_back_button())


@router.callback_query(F.data.startswith("view_tutor_feedback_"))
async def view_tutor_feedback(call: CallbackQuery):
    """Просмотр всех отзывов о выбранном репетиторе."""
    tutor_id = call.data.split("_")[-1]
    feedbacks = execute_query("""
        SELECT student_name, rating, comment
        FROM feedback
        WHERE tutor_id = ?
    """, (tutor_id,), fetchall=True)

    if feedbacks:
        response = f"📋 Отзывы о репетиторе:\n\n"
        for student_name, rating, comment in feedbacks:
            response += f"👤 {student_name}\n⭐ {rating}\n💬 {comment}\n\n"
    else:
        response = "❌ У этого репетитора пока нет отзывов."

    await call.message.edit_text(response, reply_markup=generate_back_button())
    await call.answer()


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
