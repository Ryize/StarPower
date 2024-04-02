from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import swisseph as swe
import pytz
from geopy.geocoders import Nominatim
import geopy
import random
import string
import ephem


class BaseHoroscope:

    client = None

    def __init__(self) -> None:
        load_dotenv()
        token = os.getenv('CHAT_GPT_TOKEN')
        self.client = OpenAI(api_key=token)

    def get_response(self):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request()}
            ]
            )
        return completion.choices[0].message.content


class GetHoroscope(BaseHoroscope):

    add_inf_year = ('Пожалуйста, включи описание общих тенденций, '
                    'возможностей и предостережений.'
                    'Добавь неожиданных поворотов и интригующих подробностей. '
                    'Сейчас', datetime.now().strftime('%Y'), 'год.'
                    )

    add_inf_month = ('Опиши начало месяца, потом что будет в середине'
                     'и далее чем месяц закончится.'
                     'Сейчас', datetime.now().strftime('%B'), 'месяц.'
                     )
    add_inf_week = ('Опиши начало недели, потом что будет в середине'
                    'и далее чем неделя закончится.')
    add_inf_day = 'Сейчас', datetime.now().strftime('%Y-%m-%d')

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
    }

    def __init__(self, zodiac_sign, period) -> None:
        super().__init__()
        self.zodiac_sign = zodiac_sign
        self.period = period

    def user_request(self):
        res = ("Данные возьми с сайта по астрологии."
               f"Я {self.zodiac_sign}, что меня ждет "
               f"{self.des_period[self.period][0]}? Предсказание должно "
               f"содержать {self.des_period[self.period][1]} символов. "
               f"{self.des_period[self.period][2]}")
        return res


class GetJulianDate:

    def __init__(self, date):
        self.date = date
        self.jd = self.calculation_Julian_date()

    def convertion_utc(self):
        # Конвертация в UTC
        tz = pytz.timezone('Europe/Moscow')  # Часовой пояс
        utc_time = tz.localize(self.date).astimezone(pytz.utc)
        return utc_time

    def calculation_Julian_date(self):
        # Расчет юлианской даты
        utc_time = self.convertion_utc()
        jd = swe.julday(utc_time.year, utc_time.month,
                        utc_time.day,
                        utc_time.hour + utc_time.minute / 60.0)
        return jd


class GetAstralData(GetJulianDate):

    planets = [
        ['Солнце', swe.SUN],
        ['Луна', swe.MOON],
        ['Меркурий', swe.MERCURY],
        ['Венера', swe.VENUS],
        ['Марс', swe.MARS],
        ['Юпитер', swe.JUPITER],
        ['Сатурн', swe.SATURN],
        ['Уран', swe.URANUS],
        ['Нептун', swe.NEPTUNE],
        ['Плутон', swe.PLUTO]
    ]

    zodiac_range = {
        (0, 29.999): 'Овен',
        (30, 59.999): 'Телец',
        (60, 89.999): 'Близнецы',
        (90, 119.999): 'Рак',
        (120, 149.999): 'Лев',
        (150, 179.999): 'Дева',
        (180, 209.999): 'Весы',
        (210, 239.999): 'Скорпион',
        (240, 269.999): 'Стрелец',
        (270, 299.999): 'Козерог',
        (300, 329.999): 'Водолей',
        (330, 359.999): 'Рыбы'
    }

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

    def __init__(self, date, birth_place) -> None:
        super().__init__(date)
        self.birth_place = GetAstralData.get_coordinates(birth_place)

    def calc_planet_positions(self):
        # Расчет положений планет
        planet_positions = {
            planet[0]: swe.calc_ut(
                self.jd, planet[1])[0][0] for planet in self.planets}
        return planet_positions

    def calc_planet_position(self, planet):
        # Расчет положения планеты
        planet_position = swe.calc_ut(self.jd, planet)[0][0]
        return planet_position

    def calc_houses_positions(self):
        # Расчет домов
        houses_positions = swe.houses(self.jd, self.birth_place['latitude'],
                                      self.birth_place['longitude'], b'P')[0]
        return houses_positions

    def find_zodiac_sign(self):
        pos_planets = self.calc_planet_positions()
        result = {}
        for planet, position in pos_planets.items():
            if position == 360:
                return 'Овен'
            for range, sign in self.zodiac_range.items():
                if range[0] <= position <= range[1]:
                    result[planet] = f'{planet} в знаке зодиака {sign}.\n'
        return result


class GetNatalChart(BaseHoroscope):

    description = (
        'Натальная карта должна содержать не менее 4000 символов. '
        'Повествование начинай без вступления, сразу с солнца. '
        'Не спрашивай дополнительные вопросы по консультации. '
        'Ты профессиональный астролог. Твоя цель мотивировать,'
        'успокаивать, поддерживать людей, выделять их сильные'
        'стороны, таланты и возможности для успеха. Понимание'
        'их слабостей и предложения по их преодолению. '
        'Проверь текст в нем должны быть только слова на русском языке'
        'Влияние планеты должно быть описано в 2-3 предложениях. '
        'Влияние каждого дома должно быть описано в 2-3 предложениях. '
        )

    def __init__(self, birth_date, birth_place) -> None:
        super().__init__()
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)

    def user_request(self):
        res = ("интерпретируй эти данные и предоставить информацию"
               " о влиянии этих планет и домов на  натальную карту. "
               f"дата рождения {self.birth_date}. "
               f"Место рождения {self.birth_place}. "
               f"Планеты: {self.astralData.find_zodiac_sign()}, "
               f"позиции домов {self.astralData.calc_houses_positions()}.")
        return res


class GetSpecialHoroscope(BaseHoroscope, GetJulianDate):

    zodiac_signs = [
            "Овен", "Телец", "Близнецы", "Рак",
            "Лев", "Дева", "Весы", "Скорпион",
            "Стрелец", "Козерог", "Водолей", "Рыбы"
        ]

    def __init__(self, date, zodiac_sign) -> None:
        BaseHoroscope.__init__(self)
        GetJulianDate.__init__(self, date)
        self.zodiac_sign = zodiac_sign
        self.position_moon = self.calc_position_moon()
        self.description = self.description()

    def calc_position_moon(self):
        # расчет положения луны
        position_moon = swe.calc_ut(self.jd, swe.MOON)[0][0]
        return position_moon

    def moon_in_sign(self):
        houses = list(range(1, 13))
        index = int(self.position_moon // 30)
        return (self.zodiac_signs[index], houses[index])

    def opposite_zodiac_sign(self):
        houses = list(range(1, 13))
        if self.position_moon >= 180:
            index = int((self.position_moon - 180) // 30)
        else:
            index = int((self.position_moon + 180) // 30)
        return (self.zodiac_signs[index], houses[index])

    def get_lunar_day(self):
        # Получаем следующее и предыдущее новолуние относительно указанной даты
        prev_moon = ephem.previous_new_moon(self.date)

        # Рассчитываем лунный день
        lunar_day = self.date.day - prev_moon.datetime().day + 1

        return lunar_day

    def description(self):
        des = ('Ты профессиональный астролог, сейчас ты мне делаешь '
               'предсказание, начни повествование с фразы "в этот день" '
               'Знак зодиака, в котором находится луна, указывает на '
               'положительные аспекты, а знак зодиака противоположный лунному.'
               ' указывает на отрицательные аспекты.'
               'Предсказание должно быть не менее 800 символов.'
               'В конце добавь влияние лунного дня.')
        return des

    def user_request(self):
        res = ('Составь гороскоп с особенностями характерными знаку'
               f' зодиака {self.zodiac_sign}. '
               f'Луна находится в знаке зодиака {self.moon_in_sign()[0]} '
               f'астрологический дом: {self.moon_in_sign()[1]}. Дополни '
               'информацию с учетом того что знак зодиака противоположный '
               f'лунному: {self.opposite_zodiac_sign()[0]}, астрологический '
               f'дом: {self.opposite_zodiac_sign()[1]} находится напротив и '
               'будет влиять негативно. Лунный день сейчас'
               f'{self.get_lunar_day()}. '
               'Начти без вступления и не разбивай на пункты.'
               )
        return res


# horoscope = GetHoroscope('Рак', 'today')
# print(horoscope.get_response())


# natalChart = GetNatalChart(datetime(1988, 1, 29, 17, 45), 'Смоленск')
# print(natalChart.get_response())

# getspec = GetSpecialHoroscope(datetime(2024, 4, 1), 'Водолей')
# print(getspec.get_response())

astralData = GetAstralData(datetime(1988, 6, 15, 17, 45), 'Смоленск')
print(astralData.calc_planet_position(swe.MERCURY))
print(astralData.calc_planet_positions())
# print(astralData.find_zodiac_sign())
# print(astralData.calc_houses_positions())
