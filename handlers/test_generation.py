from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import TestGenerationState
from features.test_generation import generate_test
from keyboards import generate_back_button
from .menu import send_main_menu

router = Router()


@router.callback_query(F.data == "generate_test")
async def generate_test_start(call: CallbackQuery, state: FSMContext):
    """Начало процесса генерации теста."""
    await state.clear()
    await state.set_state(TestGenerationState.waiting_for_topic)
    await call.message.edit_text("📚 Укажите тему теста:", reply_markup=generate_back_button())
    await call.answer()


@router.message(TestGenerationState.waiting_for_topic)
async def generate_test_for_topic(message: Message, state: FSMContext):
    """Генерация теста по теме."""
    topic = message.text
    await message.reply("⏳ Создаётся тест, пожалуйста, подождите...")
    try:
        test = generate_test(topic)
        await state.clear()
        await message.reply(f"✅ Тест по теме '{topic}':\n\n{test}")
    except Exception as e:
        await state.clear()
        await message.reply(f"❌ Ошибка генерации теста: {e}")
    await send_main_menu(message)


def register_handlers_test_generation(dp):
    dp.include_router(router)
