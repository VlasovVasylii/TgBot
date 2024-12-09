from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import ProblemSolvingState
from features.problem_solving import solve_problem
from keyboards import generate_back_button
from .menu import send_main_menu

router = Router()


@router.callback_query(F.data == "solve_problem")
async def solve_problem_start(call: CallbackQuery, state: FSMContext):
    """Начало процесса объяснения задачи."""
    await state.clear()
    await state.set_state(ProblemSolvingState.waiting_for_problem)
    await call.message.edit_text("🤔 Опишите задачу, которую хотите решить:", reply_markup=generate_back_button())
    await call.answer()


@router.message(ProblemSolvingState.waiting_for_problem)
async def solve_user_problem(message: Message, state: FSMContext):
    """Решение задачи."""
    problem = message.text
    await message.reply("⏳ Идёт поиск решения, пожалуйста, подождите...")
    try:
        solution = solve_problem(problem)
        await state.clear()
        await message.reply(f"✅ Решение вашей задачи:\n\n{solution}")
    except Exception as e:
        await state.clear()
        await message.reply(f"❌ Ошибка при решении задачи: {e}")
    await send_main_menu(message)


def register_handlers_problem_solving(dp):
    dp.include_router(router)
