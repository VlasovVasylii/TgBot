from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from states import ProblemSolvingState, BookingState
from datetime import timedelta, datetime

from features.problem_solving import solve_problem
from services import execute_query
from states import FeedbackState, FeedbackViewState
from .main import send_main_menu
from keyboards import generate_back_button, generate_feedback_keyboard, \
    generate_tutor_keyboard, student_menu, \
    main_menu, generate_confirm_booking_keyboard
from utils import get_user_role

router = Router()


@router.callback_query(F.data == "student_functions")
async def student_functions(call: CallbackQuery):
    """Обработка кнопки 'Для студентов'."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await call.message.edit_text("❌ Доступ запрещён. Эта функция доступна только для студентов.",
                                     reply_markup=main_menu)
        await call.answer()
        return

    await call.message.edit_text(
        "🎓 Функции для студентов:",
        reply_markup=student_menu
    )
    await call.answer()


@router.callback_query(F.data == "feedback")
async def feedback_start(call: CallbackQuery, state: FSMContext):
    """
    Начало процесса оставления отзыва.
    Проверяет, есть ли завершённые занятия у студента, и предлагает выбрать преподавателя.
    """
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await call.message.edit_text(
            "❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=generate_back_button()
        )
        await call.answer()
        return

    await state.clear()

    # Проверка завершённых занятий, для которых еще нет отзывов
    completed_bookings = execute_query("""
        SELECT DISTINCT t.id, t.name
        FROM bookings b
        JOIN tutors t ON b.tutor_id = t.id
        WHERE b.student_contact = (
            SELECT contact
            FROM students
            WHERE id = ?
        )
        AND b.status = 'approved'
        AND NOT EXISTS (
            SELECT 1 
            FROM feedback f
            WHERE f.tutor_id = t.id AND f.student_contact = b.student_contact
        )
    """, (call.from_user.id,), fetchall=True)

    if completed_bookings:
        response = "📝 Выберите ID репетитора для отзыва (вы занимались с ними):\n\n"
        for tutor_id, tutor_name in completed_bookings:
            response += f"{tutor_id}: {tutor_name}\n"

        await call.message.edit_text(response, reply_markup=generate_back_button())
        await state.set_state(FeedbackState.waiting_for_tutor_id)
    else:
        await call.message.edit_text(
            "❌ У вас нет завершённых занятий или вы уже оставили отзывы всем преподавателям.",
            reply_markup=generate_back_button()
        )
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

    # Проверяем, существует ли уже отзыв от данного студента для этого преподавателя
    existing_feedback = execute_query("""
        SELECT id FROM feedback
        WHERE tutor_id = ? AND student_contact = ?
    """, (tutor_id, message.from_user.id), fetchone=True)

    if existing_feedback:
        await message.reply("❌ Вы уже оставили отзыв для этого преподавателя.")
        await state.clear()
        await send_main_menu(message)
        return

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
async def view_feedback(call: CallbackQuery, state: FSMContext):
    """Просмотр отзывов ученика с выбором отзыва."""
    try:
        # Извлечение отзывов из базы данных
        feedbacks = execute_query("""
            SELECT f.id, t.name, f.rating, f.comment
            FROM feedback f
            JOIN tutors t ON f.tutor_id = t.id
            WHERE f.student_contact = ?
        """, (call.from_user.id,), fetchall=True)

        if feedbacks and len(feedbacks) > 0:
            # Устанавливаем состояние для FSM
            await state.set_state(FeedbackViewState.choosing_feedback)

            # Формируем текст с отзывами
            response = "📝 Ваши отзывы:\n\n"
            buttons = []
            for feedback_id, tutor_name, rating, comment in feedbacks:
                response += (
                    f"📌 Отзыв ID: {feedback_id}\n"
                    f"👨‍🏫 Преподаватель: {tutor_name}\n"
                    f"⭐ Рейтинг: {rating}\n"
                    f"💬 Комментарий: {comment if comment else 'Нет комментария'}\n\n"
                )
                # Добавляем кнопку для каждого отзыва
                button_data = f"select_feedback_{feedback_id}"
                # Ограничение длины данных кнопки (макс. 64 символа)
                if len(button_data) <= 64:
                    buttons.append(InlineKeyboardButton(
                        text=f"Выбрать отзыв {feedback_id}",
                        callback_data=button_data
                    ))
                else:
                    raise ValueError(f"Слишком длинные данные для кнопки: {button_data}")

            # Создаём клавиатуру только если есть кнопки
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])

            # Отправляем сообщение с отзывами и клавиатурой
            await call.message.edit_text(response, reply_markup=keyboard)
        else:
            # Если отзывов нет
            await call.message.edit_text(
                "❌ У вас пока нет отзывов.",
                reply_markup=generate_back_button()
            )
    except Exception as e:
        # Обработка ошибок и вывод сообщения
        await call.message.edit_text(
            f"❌ Ошибка при получении отзывов: {e}",
            reply_markup=generate_back_button()
        )
    finally:
        await call.answer()


@router.callback_query(F.data.startswith("select_feedback_"))
async def select_feedback(call: CallbackQuery, state: FSMContext):
    """Выбор отзыва для дальнейших действий."""
    try:
        # Извлечение ID отзыва из callback_data
        feedback_id = int(call.data.split("_")[2])

        # Поиск отзыва в базе данных
        feedback = execute_query("""
            SELECT id, tutor_id, rating, comment
            FROM feedback
            WHERE id = ? AND student_contact = ?
        """, (feedback_id, call.from_user.id), fetchone=True)

        if feedback:
            # Сохраняем данные в FSM
            await state.update_data(feedback_id=feedback[0], tutor_id=feedback[1])

            # Создание клавиатуры с действиями
            action_keyboard = generate_feedback_keyboard(feedback_id)

            # Отправляем отзыв с клавиатурой
            await call.message.edit_text(
                f"📝 Отзыв ID: {feedback_id}\n\n"
                f"👨‍🏫 Преподаватель ID: {feedback[1]}\n"
                f"⭐ Рейтинг: {feedback[2]}\n"
                f"💬 Комментарий: {feedback[3] if feedback[3] else 'Нет комментария'}\n\n"
                "Выберите действие:",
                reply_markup=action_keyboard
            )
        else:
            # Если отзыв не найден
            await call.message.edit_text(
                "❌ Отзыв не найден или у вас нет прав на его изменение.",
                reply_markup=generate_back_button()
            )
            print(f"Feedback ID {feedback_id} not found for user {call.from_user.id}")
    except ValueError as ve:
        # Ошибка при преобразовании ID
        await call.message.edit_text(
            "❌ Неверный формат данных для отзыва.",
            reply_markup=generate_back_button()
        )
        print(f"ValueError: {ve}")
    except Exception as e:
        # Обработка других ошибок
        await call.message.edit_text(
            f"❌ Произошла ошибка: {e}",
            reply_markup=generate_back_button()
        )
        print(f"Unhandled error: {e}")
    finally:
        await call.answer()


@router.callback_query(FeedbackViewState.choosing_action, F.data.startswith("edit_comment_"))
async def edit_comment(call: CallbackQuery, state: FSMContext):
    """Редактирование комментария."""
    data = await state.get_data()
    feedback_id = data.get("feedback_id")
    feedback = execute_query("""
        SELECT id, tutor_id, rating, comment
        FROM feedback
        WHERE id = ? AND student_contact = (
            SELECT contact
            FROM students
            WHERE id = ?
        )
    """, (feedback_id, call.from_user.id), fetchone=True)

    if feedback:
        await state.set_state(FeedbackViewState.editing_comment)
        await call.message.edit_text("💬 Напишите новый комментарий:", reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Отзыв не найден или у вас нет прав на его изменение.",
                                     reply_markup=generate_back_button())
    await call.answer()


@router.message(FeedbackViewState.editing_comment)
async def handle_new_comment(message: Message, state: FSMContext):
    """Обработка нового комментария."""
    new_comment = message.text.strip()
    data = await state.get_data()
    feedback_id = data.get("feedback_id")

    execute_query("""
        UPDATE feedback SET comment = ? WHERE id = ?
    """, (new_comment, feedback_id))

    await state.clear()
    await state.set_state(FeedbackViewState.editing_rating)
    await message.reply("✅ Комментарий успешно обновлён.", reply_markup=generate_back_button())


@router.message(FeedbackViewState.editing_rating)
async def handle_new_rating(message: Message, state: FSMContext):
    """Сохранение нового рейтинга."""
    try:
        rating = int(message.text)
        if 1 <= rating <= 5:
            data = await state.get_data()
            feedback_id = data.get("feedback_id")
            execute_query("""
                UPDATE feedback SET rating = ? WHERE id = ?
            """, (rating, feedback_id))
            await state.clear()
            await message.reply("✅ Рейтинг успешно обновлён.", reply_markup=generate_back_button())
        else:
            await message.reply("❌ Рейтинг должен быть от 1 до 5.")
    except ValueError:
        await message.reply("❌ Введите числовое значение от 1 до 5.")


@router.callback_query(FeedbackViewState.choosing_action, F.data.startswith("delete_feedback_"))
async def delete_feedback(call: CallbackQuery, state: FSMContext):
    """Удаление отзыва."""
    data = await state.get_data()
    feedback_id = data.get("feedback_id")
    feedback = execute_query("""
        SELECT id, tutor_id
        FROM feedback
        WHERE id = ? AND student_contact = (
            SELECT contact
            FROM students
            WHERE id = ?
        )
    """, (feedback_id, call.from_user.id), fetchone=True)

    if feedback:
        tutor_id = feedback[1]
        execute_query("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        update_tutor_rating(tutor_id)
        await state.clear()
        await call.message.edit_text("✅ Отзыв удалён.", reply_markup=generate_back_button())
    else:
        await call.message.edit_text("❌ Отзыв не найден или у вас нет прав на его удаление.",
                                     reply_markup=generate_back_button())
    await call.answer()


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


@router.callback_query(F.data == "calendar")
async def calendar_handler(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Календарь занятий'."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await call.message.edit_text("❌ Доступ запрещён. Эта функция доступна только для студентов.")
        await call.answer()
        return

    await state.clear()
    bookings = execute_query("""
    SELECT t.name, b.date, b.time, b.status
    FROM bookings b
    JOIN tutors t ON b.tutor_id = t.id
    WHERE b.student_contact = (
            SELECT contact
            FROM students
            WHERE id = ?
        ) AND b.status != 'approved'
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


@router.callback_query(F.data == "find_tutor")
async def find_tutor_handler(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Найти репетитора'."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await call.message.edit_text("❌ Доступ запрещён. Эта функция доступна только для студентов.")
        await call.answer()
        return

    await state.clear()
    tutors = execute_query("SELECT id, name FROM tutors", fetchall=True)
    if tutors:
        await call.message.edit_text(
            "🔍 Выберите репетитора, чтобы увидеть отзывы:",
            reply_markup=generate_tutor_keyboard(tutors)
        )
    else:
        await call.message.edit_text("❌ Репетиторы пока недоступны.", reply_markup=generate_back_button())
    await call.answer()


@router.callback_query(F.data == "solve_problem")
async def solve_problem_start(call: CallbackQuery, state: FSMContext):
    """Начало процесса объяснения задачи."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await call.message.edit_text("❌ Доступ запрещён. Эта функция доступна только для студентов.")
        await call.answer()
        return

    await state.clear()
    await state.set_state(ProblemSolvingState.waiting_for_problem)
    await call.message.edit_text("🤔 Опишите задачу, которую хотите решить:", reply_markup=generate_back_button())
    await call.answer()


@router.message(ProblemSolvingState.waiting_for_problem)
async def solve_user_problem(message: Message, state: FSMContext):
    """Решение задачи."""
    problem = message.text
    await message.reply("⏳ Идёт поиск решения, пожалуйста, подождите...")
    try:
        solution = solve_problem(problem)
        await state.clear()
        await message.reply(f"✅ Решение вашей задачи:\n\n{solution}")
    except Exception as e:
        await state.clear()
        await message.reply(f"❌ Ошибка при решении задачи: {e}")
    await send_main_menu(message, state)


@router.callback_query(F.data == "book")
async def start_booking(call: CallbackQuery, state: FSMContext):
    """Начало процесса бронирования занятия."""
    user_role = get_user_role(call.from_user.id)
    if user_role != "student":
        await call.message.edit_text(
            "❌ Доступ запрещён. Эта функция доступна только для студентов.",
            reply_markup=generate_back_button()
        )
        return

    await state.clear()
    tutors = execute_query("SELECT id, name FROM tutors", fetchall=True)
    if tutors:
        tutor_list = "\n".join([f"{tutor_id}: {name}" for tutor_id, name in tutors])
        await call.message.edit_text(
            f"📖 Доступные репетиторы:\n{tutor_list}\n\nВведите ID репетитора для бронирования:",
            reply_markup=generate_back_button()
        )
        await state.set_state(BookingState.waiting_for_tutor_id)
    else:
        await call.message.edit_text(
            "❌ Преподаватели пока недоступны.",
            reply_markup=generate_back_button()
        )


@router.message(BookingState.waiting_for_tutor_id)
async def handle_tutor_selection(message: Message, state: FSMContext):
    """Обработка выбора репетитора."""
    tutor_id = message.text.strip()
    tutor = execute_query("SELECT id, name FROM tutors WHERE id = ?", (tutor_id,), fetchone=True)
    if tutor:
        await state.update_data(tutor_id=tutor[0])
        await message.reply(
            "📅 Введите дату занятия в формате YYYY-MM-DD:",
            reply_markup=generate_back_button()
        )
        await state.set_state(BookingState.waiting_for_date)
    else:
        await message.reply("❌ Репетитор не найден. Попробуйте ещё раз.")


@router.message(BookingState.waiting_for_date)
async def handle_booking_date(message: Message, state: FSMContext):
    """Обработка даты занятия."""
    date_text = message.text.strip()
    try:
        selected_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        if selected_date >= datetime.now().date():
            await state.update_data(date=selected_date.strftime("%Y-%m-%d"))
            await message.reply("📅 Дата выбрана. Теперь укажите время в формате HH:MM:")
            await state.set_state(BookingState.waiting_for_time)
        else:
            await message.reply("❌ Нельзя выбрать прошедшую дату. Попробуйте снова.")
    except ValueError:
        await message.reply("❌ Неверный формат даты. Введите дату в формате YYYY-MM-DD.")


@router.message(BookingState.waiting_for_time)
async def handle_booking_time(message: Message, state: FSMContext):
    """Обработка времени с проверкой."""
    time_text = message.text.strip()
    try:
        datetime.strptime(time_text, "%H:%M")  # Проверяем формат времени

        data = await state.get_data()
        date = data["date"]
        selected_datetime = datetime.strptime(f"{date} {time_text}", "%Y-%m-%d %H:%M")
        if selected_datetime <= datetime.now() + timedelta(hours=1.5):
            await message.reply("❌ Бронирование возможно не менее чем за 1,5 часа до начала занятия.")
            return

        # Проверяем занятость репетитора
        tutor_id = data["tutor_id"]
        existing_booking = execute_query("""
            SELECT id FROM bookings 
            WHERE tutor_id = ? AND date = ? AND time = ?
        """, (tutor_id, date, time_text), fetchone=True)

        if existing_booking:
            await message.reply("❌ Это время уже занято у репетитора. Выберите другое время.")
            return

        await state.update_data(time=time_text)
        await state.set_state(BookingState.waiting_for_comment)
        await message.reply("💬 Добавьте комментарий для репетитора (или отправьте 'нет'):")
    except ValueError:
        await message.reply("❌ Неверный формат времени. Введите время в формате HH:MM.")


@router.message(BookingState.waiting_for_comment)
async def handle_comment(message: Message, state: FSMContext):
    """Сохранение комментария и подтверждение бронирования."""
    comment = message.text.strip()
    if comment.lower() == "нет":
        comment = ""

    await state.update_data(comment=comment)
    data = await state.get_data()

    tutor = execute_query("SELECT name FROM tutors WHERE id = ?", (data["tutor_id"],), fetchone=True)
    if tutor:
        tutor_name = tutor[0]
        await message.reply(
            f"📅 Подтверждение бронирования:\n"
            f"Репетитор: {tutor_name}\nДата: {data['date']}\nВремя: {data['time']}\nКомментарий: {comment}\n\n"
            "✅ Подтвердите или отмените бронирование.",
            reply_markup=generate_confirm_booking_keyboard()
        )
        await state.set_state(BookingState.confirm_booking)
    else:
        await message.reply("❌ Репетитор не найден. Попробуйте ещё раз.")


@router.callback_query(F.data == "confirm_booking")
async def confirm_booking(call: CallbackQuery, state: FSMContext):
    """Подтверждение бронирования."""
    data = await state.get_data()
    tutor_id = data["tutor_id"]
    date = data["date"]
    time = data["time"]
    comment = data.get("comment", "")
    student_name = call.from_user.full_name

    # Сохранение бронирования в базе данных
    execute_query("""
        INSERT INTO bookings (tutor_id, student_name, student_contact, date, time, status, comment)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (tutor_id, student_name, call.from_user.id, date, time, comment))

    await state.clear()
    await call.message.edit_text("✅ Ваше бронирование отправлено на подтверждение репетитору!",
                                 reply_markup=generate_back_button())


@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(call: CallbackQuery, state: FSMContext):
    """Обработка отмены бронирования."""
    await state.clear()
    await call.message.edit_text("❌ Бронирование отменено.", reply_markup=generate_back_button())
    await call.answer()


def update_tutor_rating(tutor_id):
    """Обновление рейтинга преподавателя."""
    # Проверка существования преподавателя
    tutor_exists = execute_query(
        "SELECT 1 FROM tutors WHERE id = ?", (tutor_id,), fetchone=True
    )
    if not tutor_exists:
        print(f"Преподаватель с ID {tutor_id} не найден.")
        return

    try:
        execute_query("""
        UPDATE tutors
        SET rating = COALESCE((SELECT AVG(rating) FROM feedback WHERE tutor_id = ?), 0),
            feedback_count = (SELECT COUNT(*) FROM feedback WHERE tutor_id = ?)
        WHERE id = ?
        """, (tutor_id, tutor_id, tutor_id))
        print(f"Рейтинг преподавателя с ID {tutor_id} успешно обновлён.")
    except Exception as e:
        print(f"Ошибка при обновлении рейтинга репетитора с ID {tutor_id}: {e}")


def register_handlers_student(dp):
    dp.include_router(router)
