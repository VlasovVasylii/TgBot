from services import execute_query


def get_user_role(user_id):
    """Получение роли пользователя."""
    # Проверяем, является ли пользователь студентом
    student_result = execute_query("SELECT id FROM students WHERE id = ?", (user_id,), fetchone=True)
    if student_result:
        return "student"

    # Проверяем, является ли пользователь преподавателем
    tutor_result = execute_query("SELECT id FROM tutors WHERE id = ?", (user_id,), fetchone=True)
    if tutor_result:
        return "tutor"

    # Если пользователь не найден ни в одной из таблиц, возвращаем None
    return None
