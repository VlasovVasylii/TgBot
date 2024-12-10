from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    waiting_for_role = State()
    waiting_for_full_name = State()
    waiting_for_contact = State()
    waiting_for_subject = State()  # Только для репетиторов


class FeedbackState(StatesGroup):
    waiting_for_feedback_choice = State()
    waiting_for_tutor_id = State()
    waiting_for_rating = State()
    waiting_for_comment = State()


class TutorState(StatesGroup):
    waiting_for_review_filter = State()
    waiting_for_topic = State()


class BookingState(StatesGroup):
    waiting_for_tutor_id = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_comment = State()
    confirm_booking = State()


class TestGenerationState(StatesGroup):
    waiting_for_topic = State()


class ProblemSolvingState(StatesGroup):
    waiting_for_problem = State()


class AdminState(StatesGroup):
    waiting_for_manage_action = State()


class FeedbackViewState(StatesGroup):
    choosing_feedback = State()
    choosing_action = State()
    editing_rating = State()
    editing_comment = State()
