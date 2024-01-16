from loader import bot
from states.search_info import UserSearchState
from database.crud import hotels_searches_from_db
from utils.rapida_sr.city_request import city_searching
from telebot.types import Message
from keyboards.inline import buttons
from datetime import datetime


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def city_asking(message: Message) -> None:
    """
    Обработчик команды для начала поиска отелей,
    записывает в хранилище часть базовой информации и запрашивает город поиска,
    устанавливает первое состояние бота
    :param message: Сообщение пользователя (команда поиска)
    """

    bot.send_message(message.chat.id, f'Привет, {message.from_user.full_name}\nВ каком городе ищем отель?')
    bot.set_state(message.chat.id, UserSearchState.city_sr)

    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        data['command'] = message.text
        data['date_time'] = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        data['user'] = message.from_user.full_name
        data['user_id'] = message.from_user.id
        data['chat_id'] = message.chat.id
        data['photo_num_sr'] = 0
        data['min_price_sr'], data['max_price_sr'], data['distance_from_sr'], data['distance_to_sr'] = 0, 0, 0, 0


@bot.message_handler(state=UserSearchState.city_sr)
def region_search(message: Message) -> None:
    """
    Обработчик первого состояние.
    Уточняет город поиска, запуская запрос к rapidapi через функцию и выводит результат в виде кнопок.
    Устанавливает следующее состояние бота
    :param message: Сообщение пользователя
    """

    bot.set_state(message.chat.id, UserSearchState.get_city_sr)
    bot.send_message(message.chat.id, 'Уточните город для поиска:',
                     reply_markup=buttons.button_for_cities(message, city_searching(message.text)))


@bot.message_handler(state=UserSearchState.min_price_sr)
def get_min_price(message: Message) -> None:
    """
    Первый обработчик для команды 'bestdeal'
    Запрашивает максимальную стоимость для искомых отелей.
    Устанавливает следующее состояние бота.
    Записывает данные в хранилище
    :param message: Сообщение пользователя
    """

    if message.text.isdigit():
        bot.send_message(message.chat.id, f'Минимальная цена за проживание: {message.text} руб.\n'
                                          f'Введите максимальную цену за сутки проживания в рублях')
        bot.set_state(message.chat.id, UserSearchState.max_price_sr)

        with bot.retrieve_data(message.chat.id) as data:
            data['min_price_sr'] = message.text
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте еще раз')


@bot.message_handler(state=UserSearchState.max_price_sr)
def get_max_price(message: Message) -> None:
    """
    Второй обработчик для команды 'bestdeal'
    Проверяет полученные данные на корректную логику.
    Запрашивает стартовую дистанцию искомых отелей от центра.
    Устанавливает следующее состояние бота.
    Записывает данные в хранилище
    :param message: Сообщение пользователя
    """

    if message.text.isdigit():

        with bot.retrieve_data(message.chat.id) as data:

            if int(message.text) > int(data['min_price_sr']):
                data['max_price_sr'] = message.text
                bot.send_message(message.chat.id, f'Максимальная цена за сутки: {message.text} руб.\n'
                                                  f'Введите диапазон расстояния,\n'
                                                  f'на котором находится отель от центра, от (км):')
                bot.set_state(message.chat.id, UserSearchState.distance_from_sr)
            else:
                bot.send_message(message.chat.id, 'Максимальная цена должна быть больше минимальной, повторите ввод')

    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте еще раз')


@bot.message_handler(state=UserSearchState.distance_from_sr)
def get_distance_from(message: Message) -> None:
    """
    Третий обработчик для команды 'bestdeal'
    Запрашивает максимальную удаленность отелей от центра.
    Устанавливает следующее состояние бота.
    Записывает данные в хранилище
    :param message: Сообщение пользователя
    """

    if message.text.isdigit():
        bot.send_message(message.chat.id, f'Диапазон расстояния до центра от: {message.text}\n'
                                          f'Теперь введите максимальное удаление от центра (км)')
        bot.set_state(message.chat.id, UserSearchState.distance_to_sr)

        with bot.retrieve_data(message.chat.id) as data:
            data['distance_from_sr'] = message.text
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте еще раз')


@bot.message_handler(state=UserSearchState.distance_to_sr)
def get_distance_to(message: Message) -> None:
    """
    Четвертый обработчик для команды 'bestdeal'
    Проверяет полученные данные на корректную логику.
    Устанавливает следующее состояние бота.
    Записывает данные в хранилище.
    Отправляет сообщение с записанными данными пользователя на проверку в виде текста и кнопки подтверждения
    :param message: Сообщение пользователя
    """

    if message.text.isdigit():

        with bot.retrieve_data(message.chat.id) as data:

            if int(message.text) > int(data['distance_from_sr']):
                data['distance_to_sr'] = message.text
                bot.send_message(message.chat.id, f'Максимальная удаленность от центра: {message.text}(км)')
                bot.send_message(message.chat.id, 'Спасибо, давайте проверим ваши критерии для поиска\n')
                text = f'Критерии поиска отелей которые вы выбрали:\n' \
                       f'Команда: {data["command"]}\nГород: {data["city_sr_name"]}\n' \
                       f'Дата заезда: {data["date_in_sr"]}, Дата выезда: {data["date_out_sr"]}\n' \
                       f'Отелей для поиска: {data["hotel_num_sr"]}, Вариант с фото: {data["photo_sr"]}\n' \
                       f'Фото для каждого отеля: {data["photo_num_sr"]},\n' \
                       f'Мин цена за сутки проживания: {data["min_price_sr"]} рублей,\n' \
                       f'Макс цена за сутки проживания: {data["max_price_sr"]} рублей,\n' \
                       f'Искать отель в диапазоне: {data["distance_from_sr"]} - {data["distance_to_sr"]} км от центра.'
                bot.send_message(message.chat.id, text)
                bot.set_state(message.chat.id, None)
            else:
                bot.send_message(message.chat.id,
                                 'Максимальная удаленность от центра должна быть больше чем минимальная ')

        bot.set_state(message.chat.id, UserSearchState.waiting_for_answer)
        bot.send_message(message.chat.id, 'Все верно?', reply_markup=buttons.button_for_answer())

    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте еще раз')


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Обработчик для команды 'history'.
    Выводит данные поисков из базы данных в виде текста и кнопки выбора варианта поиска
    :param message: Сообщение пользователя (команда)
    """

    hotels_searches = hotels_searches_from_db(message.from_user.id)
    if len(hotels_searches) == 0:
        bot.send_message(message.chat.id, 'История поиска пока пуста, воспользуйтесь для начала одной из команд поиска')
    else:
        bot.send_message(message.chat.id, f'Запросов для поиска найдено: {len(hotels_searches)}, выберите нужный:')

    for searches in hotels_searches:
        text = f'Команда: {searches.command}' \
               '\nДата и время поиска: ' \
               f'{searches.date_time.strftime("%d.%m.%Y %H:%M:%S")}' \
               f'\nМесто для поиска: {searches.city}' \
               f'\nДата заезда: {searches.date_in.strftime("%d.%m.%Y")}' \
               f'\nДата отъезда: {searches.date_out.strftime("%d.%m.%Y")}' \
               f'\nКоличеств отелей: {searches.hotels_amount}' \
               f'\nКоличество фотографий для каждого отеля: ' \
               f'{searches.photos_amount}'

        if searches.command == '/bestdeal':
            add_text = f'Минимальная цена за сутки: {searches.min_price} руб.'
            text = '\n'.join((text, add_text))
            add_text = f'Максимальная цена за сутки: {searches.max_price} руб.'
            text = '\n'.join((text, add_text))
            add_text = f'Диапазон расстояния от центра: {searches.distance_from} - {searches.distance_to} км.'
            text = '\n'.join((text, add_text))
        bot.send_message(message.chat.id, text, reply_markup=buttons.button_for_history(searches.get_id()))

    bot.set_state(message.chat.id, UserSearchState.get_from_history)
