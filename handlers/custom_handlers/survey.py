from keyboards.replay.contact import request_contact
from loader import bot
from states.contact_info import UserInfoState
from telebot.types import Message


# Тестовый опрос пользователя, данные спрятаны от пользователя

@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username}, введи свое имя')


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Спасибо записал, теперь введи свой возраст')
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Имя должно состоять только из букв')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Спасибо записал, теперь введи страну проживания')
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['age'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Возраст может быть только числом')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Спасибо записал, теперь введи город проживания')
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country'] = message.text


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    bot.send_message(message.from_user.id,
                     'Спасибо записал, теперь отправь свой номер нажав кнопку',
                     reply_markup=request_contact())
    bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone_number)
def get_contact(message: Message) -> None:
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_number'] = message.contact.phone_number

        text = f'Спасибо за предоставленную информацию, ваши данные:\n' \
               f'Имя - {data["name"]}\nВозрас - {data["age"]}\nСтрана - {data["country"]}\n' \
               f'Город - {data["city"]}\nНомер телефона - {data["phone_number"]}'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, None)
    else:
        bot.send_message(message.from_user.id, 'Чтобы отправить контактную информацию нажми на коноку')
