import sqlite3

DB_NAME = "edu_helper_bot.db"


def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'tutor', 'admin')),
        username TEXT,
        contact TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tutors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        contact TEXT NOT NULL,
        rating REAL DEFAULT 0.0,
        feedback_count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutor_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        student_contact TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        comment TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (tutor_id) REFERENCES tutors (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutor_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        FOREIGN KEY (tutor_id) REFERENCES tutors (id)
    )
    """)
    conn.commit()
    conn.close()


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


def seed_test_data():
    """Заполнение базы данных тестовыми данными."""
    tutors = [
        ("Иван Иванов", "Математика", "@ivan_tutor", 4.5),
        ("Анна Смирнова", "Физика", "@anna_tutor", 5.0)
    ]

    for tutor in tutors:
        existing_tutor = execute_query("SELECT id FROM tutors WHERE contact = ?", (tutor[2],), fetchone=True)
        if not existing_tutor:
            execute_query("INSERT INTO tutors (name, subject, contact, rating) VALUES (?, ?, ?, ?)", tutor)
