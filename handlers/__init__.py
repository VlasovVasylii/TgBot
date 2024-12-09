async def safe_edit_message_text(message, new_text, reply_markup=None):
    """Безопасное обновление текста сообщения."""
    if message.text != new_text:
        await message.edit_text(new_text, reply_markup=reply_markup)


def register_handlers(dp):
    """Регистрация всех обработчиков."""
    register_handlers_find_tutor(dp)
    register_handlers_calendar(dp)
    register_handlers_main(dp)
    register_handlers_student(dp)
    register_handlers_tutor(dp)
    register_handlers_booking(dp)
    register_handlers_problem_solving(dp)
    register_handlers_test_generation(dp)
    register_handlers_menu(dp)
    register_handlers_tutor_panel(dp)
    register_handlers_admin(dp)
    register_handlers_registration(dp)


from .main import register_handlers_main
from .student import register_handlers_student
from .tutor import register_handlers_tutor
from .find_tutor import register_handlers_find_tutor
from .calendar import register_handlers_calendar
from .booking import register_handlers_booking
from .problem_solving import register_handlers_problem_solving
from .test_generation import register_handlers_test_generation
from .menu import register_handlers_menu
from .tutor_panel import register_handlers_tutor_panel
from .admin import register_handlers_admin
from .registration import register_handlers_registration
