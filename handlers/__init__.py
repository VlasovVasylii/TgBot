from aiogram.types import Message, CallbackQuery


async def safe_edit_message_text(message, new_text, reply_markup=None):
    """Безопасное обновление текста сообщения."""
    if message.text != new_text:
        await message.edit_text(new_text, reply_markup=reply_markup)


async def send_or_edit_message(
        call_or_message,
        text: str,
        reply_markup=None,
        edit=True
):
    if isinstance(call_or_message, CallbackQuery):
        if edit:
            await call_or_message.message.edit_text(text, reply_markup=reply_markup)
        else:
            await call_or_message.message.answer(text, reply_markup=reply_markup)
        await call_or_message.answer()  # Закрытие всплывающего окна
    elif isinstance(call_or_message, Message):
        await call_or_message.reply(text, reply_markup=reply_markup)


def register_handlers(dp):
    """Регистрация всех обработчиков."""
    register_handlers_main(dp)
    register_handlers_student(dp)
    register_handlers_tutor(dp)
    register_handlers_admin(dp)
    register_handlers_registration(dp)


from .main import register_handlers_main
from .student import register_handlers_student
from .tutor import register_handlers_tutor
from .admin import register_handlers_admin
from .registration import register_handlers_registration
