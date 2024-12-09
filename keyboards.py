from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👥 Зарегистрироваться", callback_data="register"),
        InlineKeyboardButton(text="🔍 Найти репетитора", callback_data="find_tutor")
    ],
    [
        InlineKeyboardButton(text="📅 Календарь занятий", callback_data="calendar"),
        InlineKeyboardButton(text="📝 Генерация тестов", callback_data="generate_test")
    ],
    [
        InlineKeyboardButton(text="🤔 Объяснение задач", callback_data="solve_problem"),
        InlineKeyboardButton(text="📈 Панель репетитора", callback_data="tutor_panel")
    ],
    [
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
        InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="feedback")
    ],
    [
        InlineKeyboardButton(text="📖 Забронировать занятие", callback_data="book"),
        InlineKeyboardButton(text="📋 Просмотреть отзывы", callback_data="view_feedback")
    ]
])


# Панель администратора
def generate_admin_panel_keyboard():
    """Клавиатура для панели администратора."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🏫 Управление репетиторами", callback_data="manage_tutors")],
        [InlineKeyboardButton(text="👥 Управление пользователями", callback_data="manage_users")],
        [InlineKeyboardButton(text="⭐ Управление отзывами", callback_data="manage_feedbacks")],
        [InlineKeyboardButton(text="📅 Управление занятиями", callback_data="manage_bookings")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


# Фильтры отзывов
def generate_filter_reviews_keyboard():
    """Клавиатура для фильтрации отзывов по времени."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗓 За месяц", callback_data="filter_reviews_month")],
        [InlineKeyboardButton(text="🗓 За год", callback_data="filter_reviews_year")],
        [InlineKeyboardButton(text="🗓 Все отзывы", callback_data="filter_reviews_all")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


# Управление отзывами
def generate_feedback_keyboard(feedback_id):
    """Клавиатура для изменения или удаления отзыва."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_feedback_{feedback_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_feedback_{feedback_id}")
        ],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
    ])


# Список репетиторов
def generate_tutor_keyboard(tutors):
    """Клавиатура с репетиторами и возможностью просмотра их отзывов."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    for tutor_id, name in tutors:
        keyboard.add(InlineKeyboardButton(text=f"{name} (Отзывы)", callback_data=f"view_tutor_feedback_{tutor_id}"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return keyboard


# Подтверждение бронирования
def generate_confirm_booking_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking")
        ]
    ])


# Выбор роли
def generate_role_selection_keyboard():
    """Клавиатура для выбора роли при регистрации."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🎓 Студент", callback_data="student")],
        [InlineKeyboardButton(text="👨‍🏫 Репетитор", callback_data="tutor")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


# Кнопка "Назад"
def generate_back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
    ])
