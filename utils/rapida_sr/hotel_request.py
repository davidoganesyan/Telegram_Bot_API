from config_data.config import RAPID_API_KEY
from typing import Optional
from utils import json_processing
from utils.convert_to_USD import USD
from utils.rapida_sr.api_requests import api_request_sr


def hotel_search(citi_id: str, date_in: str, date_out: str,
                 min_price: Optional[int] = None,
                 max_price: Optional[int] = None):
    """
    Производит поиск отелей по выбранным критериям, делая запрос к API
    :param citi_id: id города
    :param date_in: дата заезда в отель
    :param date_out: дата выезда из отеля
    :param min_price: минимальная цена отеля за сутки
    :param max_price: максимальная цена отеля за сутки
    :return: список отелей
    """

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    day_in, month_in, year_in = map(int, date_in.split('.'))
    day_out, month_out, year_out = map(int, date_out.split('.'))

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {
            "regionId": citi_id
        },
        "checkInDate": {
            "day": day_in,
            "month": month_in,
            "year": year_in
        },
        "checkOutDate": {
            "day": day_out,
            "month": month_out,
            "year": year_out
        },
        "rooms": [
            {
                "adults": 1
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 10000,
        "sort": "PRICE_LOW_TO_HIGH",
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    if min_price and max_price:
        min_price /= USD
        max_price /= USD
        if min_price < 5:
            min_price = 5
        payload['filters'] = {
            'price': {
                'max': max_price,
                'min': min_price
            }
        }

    response = api_request_sr(method='POST', url=url, headers=headers, json=payload)
    if response:
        return json_processing.hotel_processing(response)
    else:
        return 'Ошибка поиска, попробуйте еще раз'
