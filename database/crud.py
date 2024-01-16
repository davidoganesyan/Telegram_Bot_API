from typing import List
from datetime import datetime
from database.data import db
from database.data import User, Searching, Hotel, Photo


def create_tables() -> None:
    """Создает таблицы в базе данных если они не созданы"""

    with db:
        db.create_tables([User, Searching, Hotel, Photo])


def data_to_db(data: dict) -> None:
    """Записывает данные в базу данных из переданного словаря"""

    with db.atomic():
        user = User.get_or_create(name=data['user'], user_id=data['user_id'], chat_id=data['chat_id'])[0]
        searching = Searching.create(command=data['command'], user=user,
                                     date_time=datetime.strptime(data['date_time'], '%d.%m.%Y %H:%M:%S'),
                                     photos_amount=data['photo_num_sr'], min_price=data['min_price_sr'],
                                     max_price=data['max_price_sr'], distance_from=data['distance_from_sr'],
                                     distance_to=data['distance_to_sr'], city=data['city_sr_name'],
                                     city_id=data['city_sr'],
                                     date_in=datetime.strptime(data['date_in_sr'], '%d.%m.%Y'),
                                     date_out=datetime.strptime(data['date_out_sr'], '%d.%m.%Y'),
                                     hotels_amount=data['hotel_num_sr'])

        for i_hotel in data['hotel_info']:
            hotel = Hotel.create(hotels_search=searching, name=i_hotel['name'], hotel_id=i_hotel['hotel_id'],
                                 address=i_hotel['address'], distance=i_hotel['hotel_distance'],
                                 price=i_hotel['hotel_price'], days=data['all_days'])

            for i_url in i_hotel['photos_list']:
                Photo.create(hotel=hotel, url=i_url)


def hotels_searches_from_db(user_id: int) -> List:
    """
    Извлекает историю поисков из базы данных
    :param user_id: id пользователя
    :return: история поисков
    """

    with db.atomic():
        query = Searching.select().join(User).where(User.user_id == user_id)
    query: list = list(query)

    return query


def hotel_photos_from_db(hotel: Hotel) -> List:
    """
    Извлекает фотографии для отелей из базы данных
    :param hotel: объект класса Hotel
    :return: список фотографий (url)
    """

    photos_list = list()

    with db.atomic():
        if hotel.hotels_search.photos_amount:
            photos_list = [photo.url for photo in Photo.select().where(Photo.hotel == hotel)]

    return photos_list


def hotel_data_from_db(hotels_search: Searching) -> List:
    """
    Извлекает полную информацию по записанным в базу отелям
    :param hotels_search: объект класса Searching
    :return: список с данными отеля
    """

    with db.atomic():
        query = Hotel.select().where(Hotel.hotels_search == hotels_search)

    hotels = list()
    for hotel in query:
        hotels.append(
            {'hotel': hotel.name, 'hotel_id': hotel.hotel_id, 'address': hotel.address, 'distance': hotel.distance,
             'price': hotel.price, 'days': hotel.days, 'photos_list': hotel_photos_from_db(hotel)}
        )

    return hotels
