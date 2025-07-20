from aiogram.fsm.state import State, StatesGroup

class RecruitmentStates(StatesGroup):
    """States for recruitment process"""
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_role = State()

class AdminStates(StatesGroup):
    """States for admin operations"""
    waiting_for_category = State()
    waiting_for_item_name = State()
    waiting_for_item_price = State()
    waiting_for_item_description = State()

class OrderStates(StatesGroup):
    """States for order process"""
    waiting_for_confirmation = State()
    processing_payment = State()

class SponsorStates(StatesGroup):
    """States for sponsor process"""
    waiting_for_details = State()
    waiting_for_confirmation = State()
