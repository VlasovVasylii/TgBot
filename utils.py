from db import execute_query


def get_user_role(user_id):
    """Получение роли пользователя."""
    result = execute_query("SELECT role FROM users WHERE id = ?", (user_id,), fetchone=True)
    if result:
        return result[0]
    return None
