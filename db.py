import sqlite3
from handlers.student import update_tutor_rating
from services import execute_query


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


def seed_mock_data():
    # Добавление студентов
    execute_query("""
        INSERT INTO students (id, full_name, username, contact)
        VALUES
         (1833243481, "Иван Иванов", "ivan123", "ivan@example.com"),
         (2, "Мария Смирнова", "maria321", "maria@example.com")
    """)

    # Добавление репетиторов
    execute_query("""
        INSERT INTO tutors (id, name, subject, contact, rating, feedback_count)
        VALUES
        (1, "Алексей Петров", "Математика", "alex@example.com", 0.0, 0),
        (2, "Ольга Сидорова", "Английский язык", "olga@example.com", 0.0, 0)
    """)

    # Добавление бронирований
    execute_query("""
        INSERT INTO bookings (tutor_id, student_name, student_contact, date, time, comment, status)
        VALUES
        (1, 'Иван Иванов', "ivan@example.com", '2024-12-09', '15:00', 'Подготовка к экзамену', 'approved'),
        (2, 'Иван Иванов', "ivan@example.com", '2024-12-10', '14:00', 'Подготовка к ЕГЭ', 'approved')
    """)

    # Добавление отзывов
    # execute_query("""
    #     INSERT INTO feedback (tutor_id, student_name, student_contact, rating, comment)
    #     VALUES
    #     ()
    # """)

    update_tutor_rating(1)
    update_tutor_rating(2)
