from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from db import execute_query
from keyboards import generate_back_button, generate_tutor_keyboard

router = Router()


@router.callback_query(F.data == "find_tutor")
async def find_tutor_handler(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Найти репетитора'."""
    await state.clear()
    tutors = execute_query("SELECT id, name FROM tutors", fetchall=True)
    if tutors:
        await call.message.edit_text(
            "🔍 Выберите репетитора, чтобы увидеть отзывы:",
            reply_markup=generate_tutor_keyboard(tutors)
        )
    else:
        await call.message.edit_text("❌ Репетиторы пока недоступны.", reply_markup=generate_back_button())
    await call.answer()


def register_handlers_find_tutor(dp):
    dp.include_router(router)
