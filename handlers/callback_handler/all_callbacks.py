from keyboards.inline.buttons import button_for_url
from loader import bot
from datetime import date, datetime, timedelta
from telebot.types import CallbackQuery, InputMediaPhoto
from states.search_info import UserSearchState
from keyboards.inline import buttons
from telegram_bot_calendar import DetailedTelegramCalendar
from keyboards.replay.ru_calendar import LSTEP
from utils.rapida_sr.hotel_details import cor_hotel_list, get_hotel_info
from utils.rapida_sr.hotel_request import hotel_search
from database.crud import data_to_db, Searching, hotel_data_from_db


@bot.callback_query_handler(func=None, state=UserSearchState.get_city_sr)
def city_search(call: CallbackQuery) -> None:
    """
    Первый Callback handler после выбора города из списка.
    Записывает выбранный город, готовит календарь к использованию и запускает его.
    Устанавливает следующее состояние бота
    :param call: Callback Query
    """

    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()

    with bot.retrieve_data(call.message.chat.id) as data:
        for city in data['city_list']:
            for key, value in city.items():
                if value == call.data:
                    text = city
        print(data) # потом удалить
    bot.set_state(call.message.chat.id, UserSearchState.date_in_sr)
    bot.send_message(call.message.chat.id, f'Вы выбрали город: {text["Name"]}\nТеперь выберите дату заезда')
    bot.send_message(call.message.chat.id, f'Укажите: {LSTEP[step]}', reply_markup=calendar)

    with bot.retrieve_data(call.message.chat.id) as data:
        data['city_sr'] = call.data
        data['city_sr_name'] = text['Name']
        print(data) # потом удалить


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1), state=UserSearchState.date_in_sr)
def date_in_info(call: CallbackQuery) -> None:
    """
    Второй Callback handler.
    Получает дату заезда, записывает в хранилище.
    Готовит к использованию второй календарь и запускает его.
    Устанавливает следующее состояние бота
    :param call: Callback Query
    """

    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).process(call.data)
    if not result and key:
        bot.send_message(call.message.chat.id, f'Укажите: {LSTEP[step]}', reply_markup=key)
    else:
        bot.send_message(call.message.chat.id,
                         f'Вы выбрали: {result.strftime("%d.%m.%Y")}\nТеперь выберите дату выезда')

        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_in_sr'] = result.strftime("%d.%m.%Y")
            min_date = result + timedelta(days=1)

        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=min_date).build()

        bot.set_state(call.message.chat.id, UserSearchState.date_out_sr)
        bot.send_message(call.message.chat.id, f'Укажите: {LSTEP[step]}', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2), state=UserSearchState.date_out_sr)
def date_out_info(call: CallbackQuery) -> None:
    """
    Третий Callback handler.
    Получает дату выезда, записывает в хранилище и записывает общее количество дней проживания.
    Запрашивает количество отелей для поиска, максимум 5.
    Устанавливает следующее состояние бота
    :param call: Callback Query
    """

    with bot.retrieve_data(call.message.chat.id) as data:
        min_date = (datetime.strptime(data['date_in_sr'], '%d.%m.%Y') + timedelta(days=1)).date()

    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=min_date).process(call.data)

    if not result and key:
        bot.send_message(call.message.chat.id, f'Укажите: {LSTEP[step]}', reply_markup=key)
    else:
        bot.set_state(call.message.chat.id, UserSearchState.hotel_num_sr)
        bot.send_message(call.message.chat.id,
                         f'Вы выбрали: {result.strftime("%d.%m.%Y")}\nВведите количество отелей для поиска',
                         reply_markup=buttons.hotel_markup())

        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_out_sr'] = result.strftime("%d.%m.%Y")
            data['all_days'] = (datetime.strptime(data['date_out_sr'], "%d.%m.%Y") - datetime.strptime(
                data['date_in_sr'], "%d.%m.%Y")).days


@bot.callback_query_handler(func=None, state=UserSearchState.hotel_num_sr)
def hotel_num_for_search(call: CallbackQuery) -> None:
    """
    Четвертый Callback handler.
    Получает количество отелей для поиска, записывает данные в хранилище.
    Уточняет необходимость фото для отелей (максимум 5).
    Устанавливает следующее состояние бота
    :param call: Callback Query
    """

    bot.send_message(call.message.chat.id, f'Искомое количество отелей: {call.data}')
    buttons.button_for_photo(call.message)
    bot.set_state(call.message.chat.id, UserSearchState.photo_sr)

    with bot.retrieve_data(call.message.chat.id) as data:
        data['hotel_num_sr'] = call.data


@bot.callback_query_handler(func=None, state=UserSearchState.photo_sr)
def photo_answer_info(call: CallbackQuery) -> None:
    """
    Пятый Callback handler.
    Получает ответ о необходимости фотографий, если полученный ответ: 'Да', запрашивает количество фото для отелей.
    Устанавливает следующее состояние бота или выводит данные на проверку пользователя
    :param call: Callback Query
    """

    with bot.retrieve_data(call.message.chat.id) as data:
        data['photo_sr'] = call.data

    if call.data == 'Да':
        bot.send_message(call.message.chat.id,
                         'Вы выбрали вариант с фото.\nСколько фотографий выводить для каждого отеля?',
                         reply_markup=buttons.photos_markup())
        bot.set_state(call.message.chat.id, UserSearchState.photo_num_sr)

    elif call.data == 'Нет' and data['command'] == '/bestdeal':
        bot.send_message(call.message.chat.id, 'Выберите минимальную цену за сутки проживания')
        bot.set_state(call.message.chat.id, UserSearchState.min_price_sr)

    else:
        text = f'Критерии поиска отелей, которые вы выбрали:\n' \
               f'Команда: {data["command"]}\nГород: {data["city_sr_name"]},\n' \
               f'Дата заезда: {data["date_in_sr"]}, Дата выезда: {data["date_out_sr"]}\n' \
               f'Отелей для поиска: {data["hotel_num_sr"]}, Вариант с фото: {data["photo_sr"]}\n'
        bot.send_message(call.message.chat.id, text)
        bot.set_state(call.message.chat.id, UserSearchState.waiting_for_answer)
        buttons.button_for_answer(call.message)


@bot.callback_query_handler(func=None, state=UserSearchState.photo_num_sr)
def photo_num_search(call: CallbackQuery) -> None:
    """
    Шестой Callback handler.
    Получает данные о количество фото для отелей.
    Устанавливает следующее состояние бота или выводит данные на проверку пользователя
    :param call: Callback Query
    """

    with bot.retrieve_data(call.message.chat.id) as data:
        data['photo_num_sr'] = call.data

    bot.send_message(call.message.chat.id, f'Отображаемое количество фото: {call.data}')

    if data['command'] == '/bestdeal':
        bot.send_message(call.message.chat.id, 'Выберите минимальную цену за сутки проживания в рублях')
        bot.set_state(call.message.chat.id, UserSearchState.min_price_sr)
    else:
        text = f'Критерии поиска отелей, которые вы выбрали:\n' \
               f'Команда: {data["command"]}\nГород: {data["city_sr_name"]}\n' \
               f'Дата заезда: {data["date_in_sr"]}, Дата выезда: {data["date_out_sr"]}\n' \
               f'Отелей для поиска: {data["hotel_num_sr"]}, Вариант с фото: {data["photo_sr"]}\n' \
               f'Фото для каждого отеля: {data["photo_num_sr"]}'
        bot.send_message(call.message.chat.id, text)
        bot.set_state(call.message.chat.id, UserSearchState.waiting_for_answer)
        buttons.button_for_answer(call.message)


@bot.callback_query_handler(func=None, state=UserSearchState.waiting_for_answer)
def searching(call: CallbackQuery):
    """
    Callback handler.
    Ловит ответ на корректность данных поиска, и запускает поиск отелей по всем полученным критериям.
    Отправляет пользователю результат поиска и записывает данные в базу данных
    :param call: Callback Query
    """

    with bot.retrieve_data(call.message.chat.id) as data:

        if call.data == 'Да':

            if data['command'] != '/bestdeal':
                print(data)
                bot.send_message(call.message.chat.id, 'Начинаю поиск отелей, пожалуйста подождите...')
                hotel_list = hotel_search(data['city_sr'], data['date_in_sr'], data['date_out_sr'])
                new_hotel_list = cor_hotel_list(hotel_list, data['command'], data['hotel_num_sr'])
                cor_list = get_hotel_info(new_hotel_list, data['photo_num_sr'])

            else:

                bot.send_message(call.message.chat.id, 'Начинаю поиск отелей, пожалуйста подождите...')
                hotel_list = hotel_search(data['city_sr'], data['date_in_sr'], data['date_out_sr'],
                                          int(data['min_price_sr']), int(data['max_price_sr']))
                new_hotel_list = cor_hotel_list(hotel_list, data['command'], data['hotel_num_sr'],
                                                int(data['distance_from_sr']), int(data['distance_to_sr']))
                cor_list = get_hotel_info(new_hotel_list, data['photo_num_sr'])

            for num, hotel in enumerate(cor_list):
                text = f'Отель №{num + 1}: ' \
                       f'\n\nНазвание: {hotel["name"]}' \
                       f'\nАдрес: {hotel["address"]}' \
                       f'\nРасстояние от центра: {hotel["hotel_distance"]:.2f} км.' \
                       f'\nЦена за один день: {hotel["hotel_price"]:.1f} руб.' \
                       f'\nЦена за все дни проживания ({data["all_days"]}): {hotel["hotel_price"] * data["all_days"]:.1f} руб.'

                media_group = []
                for index in range(len(hotel['photos_list'])):
                    media_group.append(
                        InputMediaPhoto(media=hotel['photos_list'][index], caption=text if index == 0 else ''))

                bot.send_media_group(call.message.chat.id, media=media_group)
                bot.send_message(call.message.chat.id, text='Детальную информацию можно узнать по ссылке ниже:',
                                 reply_markup=button_for_url(hotel))

            data['hotel_info'] = cor_list
            data_to_db(data)

        else:
            bot.send_message(call.message.chat.id, 'Тогда выберите другие критерии и попробуйте еще раз')
            bot.set_state(call.message.chat.id, None)


@bot.callback_query_handler(func=None, state=UserSearchState.get_from_history)
def get_from_history(call: CallbackQuery) -> None:
    """
    Callback handler.
    Ловит выбор пользователя из истории поиска и отправляет ему результат
    :param call: Callback Query
    """

    hotel_model_search = Searching.get_by_id(call.data)
    hotel = hotel_data_from_db(hotel_model_search)

    for num, hotel in enumerate(hotel):

        text = f'Отель №{num + 1}: ' \
               f'\n\nНазвание: {hotel["hotel"]}' \
               f'\nАдрес: {hotel["address"]}' \
               f'\nРасстояние от центра: {hotel["distance"]:.2f} км.' \
               f'\nЦена за один день: {hotel["price"]:.1f} руб.' \
               f'\nЦена за все дни проживания ({hotel["days"]}): {hotel["price"] * hotel["days"]:.1f} руб.'

        media_group = []
        for index in range(len(hotel['photos_list'])):
            media_group.append(InputMediaPhoto(media=hotel['photos_list'][index], caption=text if index == 0 else ''))

        bot.send_media_group(call.message.chat.id, media=media_group)
        bot.send_message(call.message.chat.id, text='Детальную информацию можно узнать по ссылке ниже:',
                         reply_markup=button_for_url(hotel))
