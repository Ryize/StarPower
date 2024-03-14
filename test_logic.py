from openai import OpenAI
import os
from dotenv import load_dotenv
import swisseph as swe
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
import geopy
import random
import string


class GetHoroscope:
    client = None

    day = None

    add_inf_year = ('Пожалуйста, включи описание общих тенденций, '
                    'возможностей и предостережений.'
                    'Не упоминай какой сейчас год.'
                    )

    add_inf_month = ('Опиши начало месяца, потом что будет в середине'
                     'и далее чем месяц закончится.')
    add_inf_week = ('Опиши начало недели, потом что будет в середине'
                    'и далее чем неделя закончится.')
    add_inf_day = ''
    add_inf_day_of_the_week = ('Это предсказание на число указанное ранее.'
                               'Расскажи что интересного случится в этот день')

    description = (
        'Ты профессиональный астролог.'
        'Прогнозы не должны содержать гендерных различий. '
        'Текст предсказания должен быть грамотно написан, '
        'с учетом особенностей русского языка. '
        'Добавь интересных подробностей, чтобы текст '
        'было интересно читать. Не используй общие фразы. '
        'Будь оригинальным.'
        'Не используй знак октоторп и звездочка для редактирования текста.'
        'Не разбивай текст по категориям, не делай заголовки.'
    )

    des_period = {
        'year': ['в этом году', '2500', add_inf_year],
        'month': ['в этом месяце', '1000 - 1500', add_inf_month],
        'week': ['на этой неделе', '1000 - 1500', add_inf_week],
        'today': ['сегодня', '500 - 700', add_inf_day],
        'special': [f'{day}', '500-700', add_inf_day_of_the_week]
    }

    def __init__(self, zodiac_sign, period, day=None) -> None:
        load_dotenv()
        token = os.getenv('CHAT_GPT_TOKEN')
        self.client = OpenAI(api_key=token)
        self.zodiac_sign = zodiac_sign
        self.period = period
        self.day = day

    def get_response(self):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request()}
            ]
            )
        return completion.choices[0].message.content

    def user_request(self):
        res = ("Данные возьми с сайта по астрологии."
               f"Я {self.zodiac_sign}, что меня ждет "
               f"{self.des_period[self.period][0]}? Предсказание должно "
               f"содержать {self.des_period[self.period][1]} символов. "
               f"{self.des_period[self.period][2]}")
        return res


# horoscope = GetHoroscope('Скорпион', 'today')
# print(horoscope.get_response())


class GetAstralData:

    planets = [
        ['SUN', swe.SUN],
        ['MOON', swe.MOON],
        ['MERCURY', swe.MERCURY],
        ['VENUS', swe.VENUS],
        ['MARS', swe.MARS],
        ['JUPITER', swe.JUPITER],
        ['SATURN', swe.SATURN],
        ['URANUS', swe.URANUS],
        ['NEPTUNE', swe.NEPTUNE],
        ['PLUTO', swe.PLUTO]
    ]

    @staticmethod
    def create_random_str():
        return ''.join(random.choices(
            string.ascii_letters + string.digits, k=3))

    @staticmethod
    def get_coordinates(city, user_agent='dec'):
        try:
            geolocator = Nominatim(user_agent=user_agent)
            location = geolocator.geocode(city)
            return {"latitude": location.latitude,
                    "longitude": location.longitude}
        except geopy.exc.GeopyError:
            GetAstralData.get_coordinates(
                city, user_agent=GetAstralData.create_random_str())

    def __init__(self, birth_date, birth_place) -> None:
        self.birth_date = birth_date
        self.birth_place = GetAstralData.get_coordinates(birth_place)
        self.jd = self.calculation_Julian_date()

    def convertion_utc(self):
        # Конвертация в UTC
        tz = pytz.timezone('Europe/Moscow')  # Часовой пояс
        utc_birth_time = tz.localize(self.birth_date).astimezone(pytz.utc)
        return utc_birth_time

    def calculation_Julian_date(self):
        # Расчет юлианской даты
        utc_birth_time = self.convertion_utc()
        jd = swe.julday(utc_birth_time.year, utc_birth_time.month,
                        utc_birth_time.day,
                        utc_birth_time.hour + utc_birth_time.minute / 60.0)
        return jd

    def calc_planet_positions(self):
        # Расчет положений планет
        planet_positions = {
            planet[0]: swe.calc_ut(
                self.jd, planet[1])[0][0] for planet in self.planets}
        return planet_positions

    def calc_houses_positions(self):
        # Расчет домов
        houses_positions = swe.houses(self.jd, self.birth_place['latitude'],
                                      self.birth_place['longitude'], b'P')[0]
        return houses_positions


class GetNatalChart:

    client = None

    description = (
        'Натальная карта должна содержать не менее 4000 символов. '
        'Повествование начинай без вступления, сразу с солнца. '
        'Не спрашивай дополнительные вопросы т консультации. '
        'Ты профессиональный астролог. Твоя цель мотивировать,'
        'успокаивать, поддерживать людей, выделять их сильные'
        'стороны, таланты и возможности для успеха. Понимание'
        'их слабостей и предложения по их преодолению. Людям'
        'надо рассказывать только важную для них информацию,'
        'только то что касается их непосредственно, не вдаваясь'
        'в работу астролога, но указывать дома и планеты,'
        'которые связаны с астрологическим прогнозом.')

    def __init__(self, birth_date, birth_place) -> None:
        load_dotenv()
        token = os.getenv('CHAT_GPT_TOKEN')
        self.client = OpenAI(api_key=token)
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)

    def get_response(self):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request()}
            ]
            )
        return completion.choices[0].message.content

    def user_request(self):
        res = ("интерпретируй эти данные и предоставить информацию"
               " о влиянии этих планет и домов на  натальную карту. "
               f"дата рождения {self.birth_date}. "
               f"Место рождения {self.birth_place}. "
               f"Планеты: {self.astralData.calc_planet_positions()}, "
               f"позиции домов {self.astralData.calc_houses_positions()}.")
        return res


natalChart = GetNatalChart(datetime(1988, 1, 29, 17, 45), 'Смоленск')
print(natalChart.get_response())
