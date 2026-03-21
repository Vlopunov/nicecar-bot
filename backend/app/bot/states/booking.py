from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    choosing_category = State()
    choosing_service = State()
    choosing_car_class = State()
    entering_car = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()
