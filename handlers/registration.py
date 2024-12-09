from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import RegistrationState
from db import execute_query
from keyboards import generate_role_selection_keyboard, generate_back_button, student_menu, tutor_menu, admin_menu

router = Router()


@router.callback_query(F.data == "register")
async def register_user(call: CallbackQuery, state: FSMContext):
    """
    Обработка кнопки "Зарегистрироваться".
    Проверяет, есть ли пользователь в БД, и отображает соответствующую информацию.
    """
    user_id = call.from_user.id

    existing_admin = execute_query(
        "SELECT name FROM admins WHERE id = ?", (user_id,), fetchone=True
    )
    existing_tutor = execute_query(
        "SELECT name FROM tutors WHERE id = ?", (user_id,), fetchone=True
    )
    existing_student = execute_query(
        "SELECT full_name FROM students WHERE id = ?", (user_id,), fetchone=True
    )

    if existing_student:
        await call.message.edit_text(
            f"❌ Вы уже зарегистрированы!\n"
            f"👤 Имя: {existing_student[0]}\n"
            f"📋 Статус: Студент",
            reply_markup=student_menu
        )
    elif existing_tutor:
        await call.message.edit_text(
            f"❌ Вы уже зарегистрированы!\n"
            f"👤 Имя: {existing_tutor[0]}\n"
            f"📋 Статус: Репетитор",
            reply_markup=tutor_menu
        )
    elif existing_admin:
        await call.message.edit_text(
            f"❌ Вы уже зарегистрированы!\n"
            f"👤 Имя: {existing_admin[0]}\n"
            f"📋 Статус: Администратор",
            reply_markup=admin_menu
        )
    else:
        await call.message.edit_text("👋 Вы ещё не зарегистрированы. Пожалуйста, пройдите регистрацию.")
        await state.set_state(RegistrationState.waiting_for_role)
        await call.message.edit_text("👥 Выберите вашу роль:", reply_markup=generate_role_selection_keyboard())
    await call.answer()


@router.callback_query(F.data.in_({"student", "tutor", "admin"}))
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
    elif data["role"] == "admin":
        execute_query("""
            INSERT INTO admins (id, name)
            VALUES (?, ?)
        """, (message.from_user.id, full_name))
        await state.clear()
        await message.reply("✅ Регистрация завершена! Вы зарегистрированы как Администратор.",
                            reply_markup=generate_back_button())
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
        f"✅ Регистрация завершена! Вы зарегистрированы как {'Репетитор' if role == 'tutor' else 'Студент'}.",
        reply_markup=generate_back_button()
    )


def register_handlers_registration(dp):
    dp.include_router(router)
