from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👥 Зарегистрироваться", callback_data="register"),
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
    ],
    [
        InlineKeyboardButton(text="🎓 Для студентов", callback_data="student_functions"),
        InlineKeyboardButton(text="📚 Для преподавателей", callback_data="tutor_functions")
    ],
    [
        InlineKeyboardButton(text="🛠 Для администраторов", callback_data="admin")
    ]
])

# Меню для студентов
student_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔍 Найти репетитора", callback_data="find_tutor"),
     InlineKeyboardButton(text="📅 Календарь занятий", callback_data="calendar")],
    [InlineKeyboardButton(text="📖 Забронировать занятие", callback_data="book"),
     InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="feedback")],
    [InlineKeyboardButton(text="📋 Просмотреть отзывы", callback_data="view_feedback"),
     InlineKeyboardButton(text="🤔 Объяснение задач", callback_data="solve_problem")],
    [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
])

# Меню для преподавателей
tutor_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📅 Предстоящие занятия", callback_data="upcoming_classes"),
     InlineKeyboardButton(text="📝 Генерация тестов", callback_data="generate_test")],
    [InlineKeyboardButton(text="⭐ Высокий рейтинг", callback_data="reviews_high_rating"),
     InlineKeyboardButton(text="⭐ Низкий рейтинг", callback_data="reviews_low_rating")],
    [InlineKeyboardButton(text="📊 Аналитика преподавателя", callback_data="tutor_analytics"),
     InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
])

# Меню администратора
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨‍🏫 Управление репетиторами", callback_data="manage_tutors")],
    [InlineKeyboardButton(text="👥 Управление пользователями", callback_data="manage_users")],
    [InlineKeyboardButton(text="⭐ Управление отзывами", callback_data="manage_feedbacks")],
    [InlineKeyboardButton(text="📅 Управление занятиями", callback_data="manage_bookings")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
])


def generate_tutor_keyboard(tutors, only_id=False):
    """Генерация клавиатуры с репетиторами и кнопкой назад."""
    buttons = [
        InlineKeyboardButton(text=f"{name}{'' if only_id else ' (Отзывы)'}",
                             callback_data=f"{'pick_tutor' if only_id else 'view_tutor_feedback'}_{tutor_id}")
        for tutor_id, name in tutors
    ]
    # Добавляем кнопки на клавиатуру
    ikb = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    # Кнопка "Назад"
    ikb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=ikb, row_width=2)
    return keyboard


# Фильтры отзывов
def generate_filter_reviews_keyboard():
    """Клавиатура для фильтрации отзывов."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Высокий рейтинг", callback_data="filter_reviews_high_rating"),
         InlineKeyboardButton(text="⭐ Низкий рейтинг", callback_data="filter_reviews_low_rating")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="tutor_panel")]
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


# Подтверждение бронирования
def generate_confirm_booking_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking")
        ]
    ])


# Выбор роли при регистрации
def generate_role_selection_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🎓 Студент", callback_data="_student")],
        [InlineKeyboardButton(text="👨‍🏫 Репетитор", callback_data="_tutor")],
        [InlineKeyboardButton(text="🛠 Админ", callback_data="_admin")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


# Кнопка "Назад"
def generate_back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
    ])
