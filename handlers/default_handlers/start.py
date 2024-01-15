from telebot.types import Message

from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """Хендлер с кратким описанием функционала бота"""

    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\n"
                          f"Я могу помочь с подбором отелей по всему миру)),\n"
                          f"Ну кроме России...\nДля этого просто выбери одну из команд в меню")
