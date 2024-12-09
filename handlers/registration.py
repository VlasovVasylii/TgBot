from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import RegistrationState
from db import execute_query
from keyboards import generate_role_selection_keyboard, generate_back_button, student_menu, tutor_menu

router = Router()


@router.callback_query(F.data == "register")
async def register_user(call: CallbackQuery, state: FSMContext):
    """
    Обработка кнопки "Зарегистрироваться".
    Проверяет, есть ли пользователь в БД, и отображает соответствующую информацию.
    """
    user_id = call.from_user.id
    user_data = execute_query("""
        SELECT role, full_name
        FROM users
        WHERE id = ?
    """, (user_id,), fetchone=True)

    if user_data:
        role, full_name = user_data
        if role == "student":
            menu = student_menu
            role_name = "Студент"
        elif role == "tutor":
            menu = tutor_menu
            role_name = "Репетитор"
        else:
            menu = generate_back_button()
            role_name = "Неизвестный"

        # Сообщение для зарегистрированных пользователей
        await call.message.edit_text(
            f"✅ Вы уже зарегистрированы!\n"
            f"👤 Имя: {full_name}\n"
            f"📋 Статус: {role_name}",
            reply_markup=menu
        )
    else:
        # Сообщение для незарегистрированных пользователей
        await call.message.edit_text(
            "👋 Вы ещё не зарегистрированы. Пожалуйста, пройдите регистрацию."
        )
    await state.clear()
    await call.message.edit_text("👥 Выберите вашу роль:", reply_markup=generate_role_selection_keyboard())
    await call.answer()


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
        INSERT INTO tutors (id, name, subject, contact)
        VALUES (?, ?, ?, ?)
        """, (message.from_user.id, full_name, subject, contact))
    else:
        execute_query("""
        INSERT INTO students (id, full_name, contact)
        VALUES (?, ?, ?)
        """, (message.from_user.id, full_name, contact))

    await state.clear()
    await message.reply(
        f"✅ Регистрация завершена! Вы зарегистрированы как {'репетитор' if role == 'tutor' else 'студент'}.",
        reply_markup=generate_back_button())


def register_handlers_registration(dp):
    dp.include_router(router)
