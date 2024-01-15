from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message):
    """Эхо хендлер, куда летят текстовые сообщения без указанного состояния"""

    bot.reply_to(
        message,
        "Что то не то вы написали или ответили, поэтому ловите свое сообщение обратно.\n"
        f"Вы написали, цитирую: {message.text}"
    )
