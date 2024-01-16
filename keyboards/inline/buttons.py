from keyboa import Keyboa
from loader import bot
from typing import List
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


def button_for_cities(message: Message, citi_list: List) -> InlineKeyboardMarkup:
    """
    Кнопка для уточнения городов для выбора пользователем.
    Записывает весь список городов от rapidapi в хранилище для дальнейшего использования
    :param message: Сообщение пользователя (город)
    :param citi_list: Ответ от rapidapi
    :return: InlineKeyboardMarkup
    """

    cities_button = InlineKeyboardMarkup(row_width=1)
    for citi in citi_list:
        button = InlineKeyboardButton(text=citi['Name'], callback_data=citi['city_id'])
        cities_button.add(button)
    with bot.retrieve_data(message.chat.id) as data:
        data['city_list'] = citi_list

    return cities_button


def button_for_photo() -> InlineKeyboardMarkup:
    """
    Кнопка с вопросом о необходимости фотографии для отелей
    :return: InlineKeyboardMarkup
    """

    photo_button = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    photo_button.add(button1, button2)
    return photo_button


def button_for_answer() -> InlineKeyboardMarkup:
    """
    Кнопка для ответа пользователя о корректности данных поиска
    :return: InlineKeyboardMarkup
    """

    answer_button = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    answer_button.add(button1, button2)
    return answer_button


def button_for_history(searching_id: int) -> InlineKeyboardMarkup:
    """
    Кнопка для выбора варианта из истории поиска
    :param searching_id: id варианта поиска
    :return: InlineKeyboardMarkup
    """

    history_button = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Вывести результат поиска', callback_data=searching_id)
    history_button.add(button)
    return history_button


def button_for_url(hotel) -> InlineKeyboardMarkup:
    url_button = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text='Ссылка на отель',
                                  url='https://www.hotels.com/h' + str(hotel["hotel_id"]) + '.Hotel-Information')
    url_button.add(button)
    return url_button


def amount_of() -> InlineKeyboardMarkup:
    """
    Кнопка для количества отелей и фотографий
    :return: InlineKeyboardMarkup
    """

    markup = Keyboa(items=list(range(1, 6)), items_in_row=5)
    return markup()
