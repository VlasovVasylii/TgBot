from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services import execute_query
from handlers.student import update_tutor_rating
from shared import bot

scheduler = AsyncIOScheduler()


def mark_completed_bookings():
    """Отмечает занятия как завершённые, если они начались более 1,5 часов назад."""
    now = datetime.now()
    cutoff_time = now - timedelta(hours=1.5)

    # Получение занятий, которые нужно отметить как завершённые
    bookings_to_complete = execute_query("""
        SELECT id, tutor_id
        FROM bookings
        WHERE status = 'pending' AND datetime(date || ' ' || time) <= datetime(?)
    """, (cutoff_time.strftime("%Y-%m-%d %H:%M:%S"),), fetchall=True)

    # Обновление статуса занятий
    for booking_id, tutor_id in bookings_to_complete:
        execute_query("""
            UPDATE bookings
            SET status = 'approved'
            WHERE id = ?
        """, (booking_id,))
        # Обновление аналитики преподавателя
        update_tutor_rating(tutor_id)



# Список для хранения id уже отправленных уведомлений
notified_bookings = set()

async def get_chat_id(user_id):
    """
    Получает Telegram Chat ID пользователя по его ID из таблицы user_chat_ids.
    """
    query = "SELECT chat_id FROM user_chat_ids WHERE user_id = ?"
    result = execute_query(query, (user_id,), fetchone=True)
    return result['chat_id'] if result else None

async def send_notifications():
    """
    Асинхронная функция для отправки уведомлений о занятиях студентам и преподавателям.
    """
    global notified_bookings
    bookings = get_upcoming_bookings()

    for booking in bookings:
        booking_id = booking['id']

        # Проверка, было ли отправлено уведомление для данного занятия
        if booking_id in notified_bookings:
            continue

        # Получение chat_id для студента и преподавателя
        student_chat_id = await get_chat_id(booking['student_id'])  # student_id предполагается из get_upcoming_bookings
        tutor_chat_id = await get_chat_id(booking['tutor_id'])      # tutor_id предполагается из get_upcoming_bookings

        if not student_chat_id or not tutor_chat_id:
            print(f"Ошибка: Не удалось найти chat_id для занятия {booking_id}.")
            continue

        # Формирование сообщений
        student_message = (
            f"Уважаемый(ая) {booking['student_name']},\n"
            f"Напоминаем, что ваше занятие начнется в {booking['time']} ({booking['date']}).\n"
            f"Преподаватель: {booking['name']}.\n"
            f"Контакт преподавателя: {booking['tutor_contact']}."
        )
        tutor_message = (
            f"Уважаемый(ая) {booking['name']},\n"
            f"Напоминаем, что ваше занятие с {booking['student_name']} начнется в {booking['time']} ({booking['date']}).\n"
            f"Контакт студента: {booking['student_contact']}."
        )

        # Отправка сообщений студенту и преподавателю
        try:
            await bot.send_message(chat_id=student_chat_id, text=student_message)
            await bot.send_message(chat_id=tutor_chat_id, text=tutor_message)

            # Добавление id занятия в список отправленных уведомлений
            notified_bookings.add(booking_id)

        except Exception as e:
            print(f"Ошибка при отправке уведомления для занятия {booking_id}: {e}")


def update_booking_status():
    """Изменение статуса занятий с 'pending' на 'approved', если занятие уже началось."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        execute_query("""
        UPDATE bookings
        SET status = 'approved'
        WHERE status = 'pending' AND datetime(date || ' ' || time) <= datetime(?)
        """, (current_time,))
    except Exception as e:
        print(f"Ошибка при обновлении статуса занятий: {e}")


def setup_reminders():
    """Настройка напоминаний о занятиях."""
    scheduler.add_job(send_reminders, "interval", minutes=1)
    scheduler.add_job(update_booking_status, "interval", minutes=1)
    scheduler.add_job(mark_completed_bookings, "interval", minutes=1)
    scheduler.start()
