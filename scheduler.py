from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import execute_query
from shared import bot

scheduler = AsyncIOScheduler()


def get_upcoming_bookings():
    """Получение всех занятий, которые начинаются в ближайший час."""
    now = datetime.now()
    upcoming_time = now + timedelta(hours=1)
    try:
        return execute_query("""
        SELECT b.id, b.student_name, b.student_contact, b.date, b.time, t.name, t.contact
        FROM bookings b
        JOIN tutors t ON b.tutor_id = t.id
        WHERE datetime(b.date || ' ' || b.time) BETWEEN datetime(?) AND datetime(?)
        """, (now.strftime("%Y-%m-%d %H:%M:%S"), upcoming_time.strftime("%Y-%m-%d %H:%M:%S")), fetchall=True)
    except Exception as e:
        print(f"Ошибка при получении предстоящих занятий: {e}")
        return []


async def send_reminders():
    """Отправка напоминаний."""
    bookings = get_upcoming_bookings()
    if not bookings:
        return

    for booking in bookings:
        student_contact, tutor_contact = booking[2], booking[6]
        try:
            # Отправка сообщения студенту
            await bot.send_message(
                student_contact,
                f"📅 Напоминание: занятие с {booking[5]} через 1 час.\nДата: {booking[3]}, время: {booking[4]}"
            )

            # Отправка сообщения преподавателю
            await bot.send_message(
                tutor_contact,
                f"📅 Напоминание: занятие со студентом {booking[1]} через 1 час.\n"
                f"Дата: {booking[3]}, время: {booking[4]}"
            )

        except Exception as e:
            print(f"Ошибка при отправке уведомления: {e}")


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
    scheduler.start()
