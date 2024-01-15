from telebot.handler_backends import State, StatesGroup


class UserSearchState(StatesGroup):
    """Класс состояний для поиска отеля"""

    city_sr = State()
    get_city_sr = State()
    date_in_sr = State()
    date_out_sr = State()
    hotel_num_sr = State()
    photo_sr = State()
    photo_num_sr = State()
    min_price_sr = State()
    max_price_sr = State()
    distance_from_sr = State()
    distance_to_sr = State()
    waiting_for_answer = State()
    get_from_history = State()
