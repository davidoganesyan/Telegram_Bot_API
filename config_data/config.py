import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Справка"),
    ('lowprice', 'Самые дешевые отели в городе'),
    ('highprice', 'Самые дорогие отели в городе'),
    ('bestdeal', 'Наиболее подходящие по цене и расположению от центра'),
    ('history', 'История поиска отелей')
)
