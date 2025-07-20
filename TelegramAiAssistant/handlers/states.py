from aiogram.fsm.state import State, StatesGroup

class SponsorStates(StatesGroup):
    waiting_for_minecraft_name = State()
    waiting_for_hours_info = State()
    waiting_for_forward_message = State()
    waiting_for_payment_photo = State()

class OrderStates(StatesGroup):
    waiting_for_payment_photo = State()
    waiting_for_minecraft_name = State()

class AdminStates(StatesGroup):
    waiting_for_item_name = State()
    waiting_for_item_price = State()
    waiting_for_item_description = State()
    waiting_for_admin_id = State()
    waiting_for_category_name = State()
    waiting_for_sponsor_channel = State()

    # Category management
    waiting_for_new_category = State()
    waiting_for_category_name = State()

    # Edit item states
    waiting_for_edit_price = State()
    waiting_for_edit_description = State()

class OrderStates(StatesGroup):
    waiting_for_payment_photo = State()

class RecruitmentStates(StatesGroup):
    waiting_for_minecraft_name = State()
    waiting_for_telegram = State()
    waiting_for_presentation = State()
    waiting_for_reason = State()
    waiting_for_experience = State()
    waiting_for_hours = State()
    waiting_for_advice = State()
    waiting_for_bad_employee = State()
    waiting_for_additional = State()
    waiting_for_additional_text = State()

class ReplyStates(StatesGroup):
    waiting_for_reply_message = State()