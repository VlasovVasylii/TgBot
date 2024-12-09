from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import RegistrationState
from db import execute_query
from keyboards import generate_role_selection_keyboard, generate_back_button

router = Router()


@router.message(F.text.startswith("/register"))
async def start_registration(message: Message, state: FSMContext):
    """Начало процесса регистрации."""
    await state.clear()
    await state.set_state(RegistrationState.waiting_for_role)
    await message.reply("👥 Выберите вашу роль:", reply_markup=generate_role_selection_keyboard())


@router.callback_query(F.data.in_({"student", "tutor"}))
async def set_user_role(call: CallbackQuery, state: FSMContext):
    """Установка роли пользователя."""
    role = call.data
    await state.update_data(role=role)
    await state.set_state(RegistrationState.waiting_for_full_name)
    await call.message.edit_text("✍️ Введите ваше полное имя:")
    await call.answer()


@router.message(RegistrationState.waiting_for_full_name)
async def set_user_full_name(message: Message, state: FSMContext):
    """Сохранение имени пользователя."""
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)

    data = await state.get_data()
    if data["role"] == "tutor":
        await state.set_state(RegistrationState.waiting_for_subject)
        await message.reply("📚 Укажите предмет, который вы преподаёте:")
    else:
        await state.set_state(RegistrationState.waiting_for_contact)
        await message.reply("📞 Введите ваш контакт (например, номер телефона):")


@router.message(RegistrationState.waiting_for_subject)
async def set_tutor_subject(message: Message, state: FSMContext):
    """Сохранение предмета репетитора."""
    subject = message.text.strip()
    await state.update_data(subject=subject)
    await state.set_state(RegistrationState.waiting_for_contact)
    await message.reply("📞 Введите ваш контакт (например, номер телефона):")


@router.message(RegistrationState.waiting_for_contact)
async def save_user_data(message: Message, state: FSMContext):
    """Сохранение данных пользователя в базу."""
    contact = message.text.strip()
    data = await state.get_data()

    role = data["role"]
    full_name = data["full_name"]

    if role == "tutor":
        subject = data["subject"]
        execute_query("""
        INSERT INTO tutors (name, subject, contact)
        VALUES (?, ?, ?)
        """, (full_name, subject, contact))
    else:
        execute_query("""
        INSERT INTO users (id, full_name, role, contact)
        VALUES (?, ?, ?, ?)
        """, (message.from_user.id, full_name, role, contact))

    await state.clear()
    await message.reply(
        f"✅ Регистрация завершена! Вы зарегистрированы как {'репетитор' if role == 'tutor' else 'студент'}.",
        reply_markup=generate_back_button())


def register_handlers_registration(dp):
    dp.include_router(router)
