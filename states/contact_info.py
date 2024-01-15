from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    """Класс для тестового опроса пользователя, скрыт от пользователя"""

    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()
