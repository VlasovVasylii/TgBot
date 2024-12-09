import sqlite3

DB_NAME = "edu_helper_bot.db"


def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            username TEXT,
            contact TEXT
        )
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tutors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        contact TEXT NOT NULL,
        rating REAL DEFAULT 0.0,
        feedback_count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
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

    # Таблица отзывов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_contact TEXT NOT NULL,
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


def seed_mock_data():
    # Добавление студентов
    execute_query("""
        INSERT INTO students (id, full_name, contact)
        VALUES
        (1, 'Тестовый Студент', 'student_contact')
    """)

    # Добавление репетиторов
    execute_query("""
        INSERT INTO tutors (name, subject, contact, rating, feedback_count)
        VALUES
        ('Репетитор Иван', 'Математика', '@ivan_tutor', 4.5, 2),
        ('Репетитор Анна', 'Физика', '@anna_tutor', 5.0, 1)
    """)

    # Добавление бронирований
    execute_query("""
        INSERT INTO bookings (tutor_id, student_name, student_contact, date, time, comment, status)
        VALUES
        (1, 'Тестовый Студент', 'student_contact', '2024-12-15', '15:00', 'Подготовка к экзамену', 'pending'),
        (2, 'Тестовый Студент', 'student_contact', '2024-12-16', '14:00', 'Подготовка к ЕГЭ', 'approved')
    """)

    # Добавление отзывов
    execute_query("""
        INSERT INTO feedback (tutor_id, student_name, student_contact, rating, comment)
        VALUES
        (1, 'Тестовый Студент', 'student_contact', 5, 'Отличный преподаватель!'),
        (2, 'Тестовый Студент', 'student_contact', 4, 'Хорошо объясняет.')
    """)
