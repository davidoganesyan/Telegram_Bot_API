import json
from typing import Optional, Any
from utils.convert_to_USD import USD


def city_processing(response: str) -> Optional[Any]:
    """
    Производит десериализацию json ответа от API и выбирает нужные города
    :param response: Json ответ от API
    :return: Список городов или ошибку
    """

    cities_list = list()
    resp_data = json.loads(response)
    if not resp_data:
        return 'Результат по вашему запросу пуст, попробуйте еще раз'
    for sr in resp_data['sr']:
        if sr['type'] == 'CITY' or sr['type'] == 'NEIGHBORHOOD':
            find_cite = dict()
            if len(sr['regionNames']['fullName']) > 32:
                find_cite['Name'] = sr['regionNames']['fullName'][:33] + '...'
            else:
                find_cite['Name'] = sr['regionNames']['fullName']
            find_cite['city_id'] = sr['gaiaId']
            cities_list.append(find_cite)

    return cities_list


def hotel_processing(response: str) -> Optional[Any]:
    """
    Производит десериализацию json ответа от API и выбирает нужные отели
    :param response: Json ответ от API
    :return: Список отелей подпадающий под критерии
    """

    resp_data = json.loads(response)
    hotel_list = list()
    if not resp_data:
        return 'Результат по вашему запросу пуст, попробуйте еще раз'
    for num_id in resp_data['data']['propertySearch']['properties']:
        find_hotel = dict()
        find_hotel['name'] = num_id['name']
        find_hotel['hotel_id'] = num_id['id']
        find_hotel['hotel_price'] = round(num_id['price']['lead']['amount'] * USD, 2)
        find_hotel['hotel_distance'] = round(num_id['destinationInfo']['distanceFromDestination']['value'] * 1.0693, 2)
        hotel_list.append(find_hotel)
    return hotel_list
