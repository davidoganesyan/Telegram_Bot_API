from telebot.types import ReplyKeyboardMarkup, KeyboardButton


# Тестовый запрос контактов пользователя, скрыт от пользователя

def request_contact() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Отправить контакт', request_contact=True))
    return keyboard
