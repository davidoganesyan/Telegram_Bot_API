from peewee import *
import os

db = SqliteDatabase(os.path.join('database', 'data.db'))


class BaseModel(Model):
    """"Класс базовой модели для ORM"""

    class Meta:
        database = db


class User(BaseModel):
    """Класс Пользователь (для ORM)"""

    class Meta:
        db_table = 'Users'

    name = CharField()
    user_id = IntegerField(unique=True)
    chat_id = IntegerField()


class Searching(BaseModel):
    """Класс Поиск отелей (для ORM)"""

    class Meta:
        db_table = 'Searching Hotel'

    command = CharField()
    user = ForeignKeyField(User)
    date_time = DateTimeField()
    city = CharField()
    city_id = CharField()
    date_in = DateField()
    date_out = DateField()
    hotels_amount = IntegerField()
    photos_amount = IntegerField()
    min_price = IntegerField(null=True)
    max_price = IntegerField(null=True)
    distance_from = IntegerField(null=True)
    distance_to = IntegerField(null=True)


class Hotel(BaseModel):
    """ Класс Отель (для ORM)"""

    class Meta:
        db_table = 'Found hotels'

    hotels_search = ForeignKeyField(Searching)
    name = CharField()
    hotel_id = IntegerField()
    address = CharField()
    distance = FloatField()
    price = FloatField()
    days = IntegerField()


class Photo(BaseModel):
    """Класс Фото (для ORM)"""

    class Meta:
        db_table = 'Photo for hotel'

    hotel = ForeignKeyField(Hotel)
    url = CharField()
