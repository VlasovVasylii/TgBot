import sqlite3

DB_NAME = "edu_helper_bot.db"


def execute_query(query, params=(), fetchone=False, fetchall=False):
    """Универсальная функция для выполнения запросов."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        conn.commit()
        return result
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        raise
    finally:
        conn.close()
