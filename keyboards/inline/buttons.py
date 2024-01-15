from loader import bot
from keyboa import Keyboa
from typing import List
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


def button_for_cities(message: Message, citi_list: List) -> None:
    """
    Кнопка для уточнения городов для выбора пользователем.
    Записывает весь список городов от rapidapi в хранилище для дальнейшего использования
    :param message: Сообщение пользователя (город)
    :param citi_list: Ответ от rapidapi
    :return: None
    """

    cities_button = InlineKeyboardMarkup(row_width=1)
    for citi in citi_list:
        button = InlineKeyboardButton(text=citi['Name'], callback_data=citi['city_id'])
        cities_button.add(button)
    bot.send_message(message.chat.id, 'Уточните город', reply_markup=cities_button)
    with bot.retrieve_data(message.chat.id) as data:
        data['city_list'] = citi_list


def button_for_photo(message: Message) -> None:
    """
    Кнопка с вопросом о необходимости фотографии для отелей
    :param message: Сообщение пользователя
    :return: None
    """

    photo_button = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    photo_button.add(button1, button2)
    bot.send_message(message.chat.id, 'Нужны фотографии отелей?', reply_markup=photo_button)


def button_for_answer(message: Message) -> None:
    """
    Кнопка для ответа пользователя о корректности данных поиска
    :param message: Сообщение пользователя
    :return: None
    """

    answer_button = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Да', callback_data='Да')
    button2 = InlineKeyboardButton('Нет', callback_data='Нет')
    answer_button.add(button1, button2)
    bot.send_message(message.chat.id, 'Все верно?', reply_markup=answer_button)


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


photos_markup = Keyboa(items=list(range(1, 6)), items_in_row=5)  # Кнопка для количества фотографий
hotel_markup = Keyboa(items=list(range(1, 6)), items_in_row=5)  # Кнопка для количества отелей
