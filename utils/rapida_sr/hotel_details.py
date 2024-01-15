import json
from typing import List
from config_data.config import RAPID_API_KEY
from utils.rapida_sr.api_requests import api_request_sr


def cor_hotel_list(hotel_list: List, command: str, hotel_amount: int, distance_from=None, distance_to=None) -> List:
    """
    Фильтрует и сортирует изначальный список отелей, подпадающий под критерии поиска
    :param hotel_list: Общий список отелей из ответа API, обработанный функцией 'hotel_processing'
    :param command: Выбранная команда поиска
    :param hotel_amount: Количество отелей, выбранное пользователем
    :param distance_from: Минимальная удаленность отеля от центра
    :param distance_to: Максимальная удаленность отеля от центра
    :return: Корректный список отелей
    """

    new_hotel_list = []
    if command == '/highprice':
        new_hotel_list = sorted(hotel_list, key=lambda elem: elem['hotel_price'], reverse=True)[:int(hotel_amount)]
    elif command == '/lowprice':
        new_hotel_list = hotel_list[:int(hotel_amount)]
    else:
        for hotel in hotel_list:
            if distance_from <= hotel['hotel_distance'] <= distance_to:
                new_hotel_list.append(hotel)
    return new_hotel_list[:int(hotel_amount)]


def get_hotel_info(hotel_list: List, photo_amount: int) -> List:
    """
    Делает запрос к API по выбранному списку отелей, для получения детальной информации по ним
    :param hotel_list: корректный список отелей из функции 'cor_hotel_list'
    :param photo_amount: количество фото для отелей
    :return: список отелей с деталями и фото
    """

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    for hotel in hotel_list:
        payload['propertyId'] = hotel['hotel_id']
        hotel['photos_list'] = list()
        address = None
        response = api_request_sr(method='POST', url=url, headers=headers, json=payload)

        if response:
            result = json.loads(response)
            address = result['data']['propertyInfo']['summary']['location']['address']['addressLine']
            images = result['data']['propertyInfo']['propertyGallery']['images']

            count = 0
            for image in images:
                if count < int(photo_amount):
                    hotel['photos_list'].append(image['image']['url'])
                else:
                    break
                count += 1

        hotel['address'] = address
    return hotel_list
