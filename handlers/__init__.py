async def safe_edit_message_text(message, new_text, reply_markup=None):
    """Безопасное обновление текста сообщения."""
    if message.text != new_text:
        await message.edit_text(new_text, reply_markup=reply_markup)


def register_handlers(dp):
    """Регистрация всех обработчиков."""
    register_handlers_main(dp)
    register_handlers_menu(dp)
    register_handlers_student(dp)
    register_handlers_tutor(dp)
    register_handlers_admin(dp)
    register_handlers_registration(dp)


from .main import register_handlers_main
from .student import register_handlers_student
from .tutor import register_handlers_tutor
from .menu import register_handlers_menu
from .admin import register_handlers_admin
from .registration import register_handlers_registration
