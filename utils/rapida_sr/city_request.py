from config_data.config import RAPID_API_KEY
from typing import Optional, Any
from utils import json_processing
from utils.rapida_sr.api_requests import api_request_sr


def city_searching(city: str) -> Optional[Any]:
    """
    Производит поиск городов через API по названию, полученному от пользователя
    :param city: Сообщение пользователя (город)
    :return: Список городов для выбора или ошибку поиска
    """

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = api_request_sr(method='GET', url=url, headers=headers, params=querystring)
    if response:
        return json_processing.city_processing(response)
    else:
        return 'Ошибка поиска, попробуйте еще раз'
