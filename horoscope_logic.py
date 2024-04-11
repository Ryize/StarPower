"""
Этот модуль предназначен для генерации гороскопов с использованием
астрологических данных и API OpenAI.

Обзор Классов

BaseHoroscope
Базовый класс, который использует API OpenAI для генерации текстовых ответов
на основе предварительно заданных запросов. Этот класс загружает токен API из
переменных окружения и выполняет запросы к GPT-3.5-turbo модели для генерации
гороскопов.

GetHoroscope
Класс, наследуемый от BaseHoroscope, предназначенный для получения гороскопа
для конкретного знака зодиака на определённый период
(год, месяц, неделя, день).Включает в себя динамическую подстройку запроса
в зависимости от выбранного периода.

GetJulianDate
Класс для расчёта юлианской даты из григорианской. Используется для
астрологических расчётов, связанных с позиционированием планет и лунных фаз.

GetAstralData
Добавляет возможность расчёта положений планет и астрологических домов на
момент рождения. Используется для анализа натальных карт.

GetNatalChart
Класс для создания запросов на генерацию натальной карты с использованием
данных, полученных от GetAstralData. Основывается на базовых астрологических
данных пользователя, включая дату и место рождения.

GetSpecialHoroscope
Специализированный класс для создания гороскопов с учётом текущего положения
Луны, лунного дня и противоположного знака зодиака. Интегрирует
астрологические и астрономические данные для более глубокого анализа.

Общие Зависимости
python-dotenv: Для загрузки переменных окружения.
ephem: Для расчётов астрономических и астрологических данных.
pytz: Для работы с часовыми поясами.
swisseph: Библиотека для расчётов положений планет и астрологических домов.
geopy: Для определения географических координат по названию города.
OpenAI: SDK для взаимодействия с GPT-3.
"""

import os
import random
import string
from datetime import datetime

import ephem
import geopy
import pytz
import swisseph as swe
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from openai import OpenAI


class BaseHoroscope:
    """
    Базовый класс для создания гороскопов с использованием OpenAI API.

    Отвечает за инициализацию клиента OpenAI с API-ключом, загруженным из
    переменных окружения,
    и генерацию текстовых ответов на основе предопределённых описаний и
    запросов пользователя.

    Атрибуты:
        client (OpenAI): Клиент для обращения к OpenAI API.

    Методы:
        __init__(self) -> None: Инициализирует клиента OpenAI.
        get_response(self) -> str: Генерирует гороскоп и возвращает текстовый
        ответ.
    """

    client = None

    def __init__(self) -> None:
        """
        Конструктор класса, который загружает API-ключ из переменных окружения
        и инициализирует клиента OpenAI.
        """
        load_dotenv()
        token = os.getenv('CHAT_GPT_TOKEN')
        self.client = OpenAI(api_key=token)

    def get_response(self) -> str:
        """
        Создаёт и отправляет запрос в OpenAI API для генерации гороскопа,
        используя предопределённые описание и запрос пользователя.

        Возвращает:
            Строка с текстом гороскопа, сгенерированного моделью OpenAI.
        """
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request()}
            ]
            )
        return completion.choices[0].message.content


class GetHoroscope(BaseHoroscope):
    """
    Класс расширяет функциональность BaseHoroscope, предоставляя
    специализированные методы для генерации гороскопов на основе знака зодиака
    пользователя и заданного временного периода (год, месяц, неделя, день).

    Атрибуты
    add_inf_year: Дополнительная информация для годового гороскопа.
    add_inf_month: Дополнительная информация для месячного гороскопа.
    add_inf_week: Дополнительная информация для недельного гороскопа.
    add_inf_day: Дополнительная информация для дневного гороскопа.
    description: Описание задания для модели GPT-3, общее для всех запросов.
    des_period: Словарь, связывающий период с требованиями к гороскопу.
    zodiac_sign: Знак зодиака пользователя.
    period: Запрошенный временной период для гороскопа.

    Методы
    __init__(self, zodiac_sign: str, period: str) -> None:
    Инициализирует экземпляр класса с указанным знаком зодиака и периодом.

    user_request(self) -> str:
    Сформирует и вернет запрос пользователя, который будет отправлен в модель
    GPT-3 для генерации гороскопа.
    """

    add_inf_year = ('Пожалуйста, включи описание общих тенденций, '
                    'возможностей и предостережений.'
                    'Добавь неожиданных поворотов и интригующих подробностей. '
                    'Сейчас', datetime.now().strftime('%Y'), 'год. '
                    'Убедись что в твоем ответе указан только этот год.'
                    )

    add_inf_month = ('Опиши начало месяца, потом что будет в середине'
                     'и далее чем месяц закончится.'
                     'Сейчас', datetime.now().strftime('%B'), 'месяц. '
                     'Убедись что в твоем ответе указан только этот месяц'
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

    def __init__(self, zodiac_sign: str, period: str) -> None:
        """
        Инициализирует объект класса GetHoroscope.

        Параметры:
            zodiac_sign (str): Знак зодиака пользователя.
            period (str): Период времени, для которого требуется гороскоп.
            Допустимые значения: "year", "month", "week", "today".

        Возвращает:
            None.
        """
        super().__init__()
        self.zodiac_sign = zodiac_sign
        self.period = period

    def user_request(self) -> str:
        """
    Формирует запрос пользователя для генерации гороскопа.

    Запрос составляется на основе знака зодиака и периода, указанных при
    инициализации объекта, с учетом дополнительной информации, специфичной для
    каждого временного периода.

    Возвращает:
        res (str): Строка запроса, которая будет отправлена в модель OpenAI
        для генерации гороскопа. Содержит инструкции и ограничения по
        количеству символов, соответствующие выбранному периоду.
    """
        res = ("Данные возьми с сайта по астрологии."
               f"Я {self.zodiac_sign}, что меня ждет "
               f"{self.des_period[self.period][0]}? Предсказание должно "
               f"содержать {self.des_period[self.period][1]} символов. "
               f"{self.des_period[self.period][2]}")
        return res


class GetJulianDate:
    """
    Класс предназначен для расчета юлианской даты,.

    Атрибуты
    date: Дата в григорианском календаре, для которой будет рассчитана
    юлианская дата.
    jd: Рассчитанная юлианская дата.
    Методы
    __init__(self, date: datetime) -> None:
    Инициализирует экземпляр класса с указанной датой.

    convertion_utc(self) -> datetime:
    Конвертирует заданную дату во временную зону UTC.

    calculation_Julian_date(self) -> float:
    Рассчитывает и возвращает юлианскую дату для заданной даты в UTC.
    """

    def __init__(self, date) -> None:
        """
        Инициализация экземпляра класса GetJulianDate.

        Параметры:
            date (datetime.datetime): григорианская дата.
        Атрибуты:
            self.date (datetime.datetime): григорианская дата.
            self.jd (float): Рассчитанная юлианская дата.
    """
        self.date = date
        self.jd = self.calculation_Julian_date()

    def convertion_utc(self) -> datetime:
        """
        Конвертирует сохраненную григорианскую дату в UTC.

        Возвращает:
            utc_time (datetime.datetime): Дата и время в формате UTC.
        """
        tz = pytz.timezone('Europe/Moscow')  # Часовой пояс
        utc_time = tz.localize(self.date).astimezone(pytz.utc)
        return utc_time

    def calculation_Julian_date(self) -> tuple:
        """
        Рассчитывает юлианскую дату на основе конвертированной в UTC
        григорианской даты.

        Возвращает:
            jd (tuple): Юлианская дата, соответствующая заданной
            григорианской дате.
        """
        utc_time = self.convertion_utc()
        jd = swe.julday(utc_time.year, utc_time.month,
                        utc_time.day,
                        utc_time.hour + utc_time.minute / 60.0)
        return jd


class GetAstralData(GetJulianDate):
    """
    Добавляет функционал для расчета астрологических данных, таких как
    положения планет и астрологических домов, на основе даты и места рождения.

    Атрибуты
    planets: Список планет и их идентификаторов в библиотеке Swiss Ephemeris.
    zodiac_range: Словарь, определяющий диапазоны градусов для каждого знака
    зодиака.
    birth_place: Координаты места рождения.
    Методы
    __init__(self, date: datetime.datetime, birth_place: str) -> None
    Инициализирует объект с датой и местом рождения, автоматически рассчитывая
    координаты места рождения и юлианскую дату.

    create_random_str() -> str
    Генерирует случайную строку для использования в качестве user-agent при
    запросах к геолокационным сервисам.

    get_coordinates(city: str, user_agent: str = 'dec') -> dict
    Определяет географические координаты места рождения на основе его названия.

    calc_planet_positions(self) -> dict[str, float]
    Рассчитывает положения всех интересующих планет на момент рождения.

    calc_planet_position(self, planet: int) -> float
    Рассчитывает положение конкретной планеты на момент рождения.

    calc_houses_positions(self) -> list[float]
    Рассчитывает положения астрологических домов на момент рождения.

    find_zodiac_sign(self) -> dict[str, str]
    Определяет знак зодиака для каждой планеты на момент рождения.
    """

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
    def create_random_str() -> str:
        """
        Генерирует случайную строку длиной 3 символа, состоящую из букв и цифр.

        Возвращает:
            Строка, используемая в качестве user-agent.
        """
        return ''.join(random.choices(
            string.ascii_letters + string.digits, k=3))

    @staticmethod
    def get_coordinates(city: str, user_agent='dec') -> dict:
        """
        Ищет географические координаты города.

        Параметры:
            city (str): Название города.
            user_agent (str): Идентификатор user-agent для запросов к
            геолокационному API.

        Возвращает:
            Словарь с ключами "latitude" и "longitude", содержащий
            географические координаты города.
        """
        try:
            geolocator = Nominatim(user_agent=user_agent)
            location = geolocator.geocode(city)
            return {"latitude": location.latitude,
                    "longitude": location.longitude}
        except geopy.exc.GeopyError:
            GetAstralData.get_coordinates(
                city, user_agent=GetAstralData.create_random_str())

    def __init__(self, date, birth_place) -> None:
        """
        Инициализирует экземпляр класса для расчета астрологических данных.

        Параметры:
            date (datetime): Дата и время рождения.
            birth_place (str): Место рождения.
        """
        super().__init__(date)
        self.birth_place = GetAstralData.get_coordinates(birth_place)

    def calc_planet_positions(self) -> dict:
        """
        Рассчитывает положения всех зарегистрированных планет на момент
        рождения.

        Возвращает:
            Словарь с названиями планет в качестве ключей и их положениями в
            градусах зодиакального круга в качестве значений.
        """
        planet_positions = {
            planet[0]: swe.calc_ut(
                self.jd, planet[1])[0][0] for planet in self.planets}
        return planet_positions

    def calc_planet_position(self, planet: int) -> float:
        """
        Рассчитывает положение указанной планеты на момент рождения.

        Параметры:
            planet (int): Идентификатор планеты в системе Swiss Ephemeris.

        Возвращает:
            Положение планеты в градусах зодиакального круга.
        """
        planet_position = swe.calc_ut(self.jd, planet)[0][0]
        return planet_position

    def calc_houses_positions(self) -> list:
        """
        Рассчитывает положения астрологических домов на момент рождения.

        Возвращает:
            Список положений начал астрологических домов в градусах
            зодиакального круга.
        """
        houses_positions = swe.houses(self.jd, self.birth_place['latitude'],
                                      self.birth_place['longitude'], b'P')[0]
        return houses_positions

    def find_zodiac_sign(self) -> dict:
        """
        Определяет знаки зодиака для всех зарегистрированных планет на момент
        рождения.

        Возвращает:
            Словарь с названиями планет в качестве ключей и знаками зодиака в
            качестве значений.
        """
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
    """
    Класс предназначен для генерации текста натальной карты.

    Атрибуты
    description: Статическое описание задачи для OpenAI, подчеркивающее
    ключевые аспекты и цели анализа натальной карты.
    birth_date: Дата и время рождения.
    birth_place: Место рождения.
    astralData: Экземпляр класса GetAstralData для выполнения астрологических
    расчетов.

    Методы
    __init__(self, birth_date: datetime.datetime, birth_place: str) -> None
    Инициализирует экземпляр класса, устанавливая необходимые атрибуты для
    расчета и анализа натальной карты.

    user_request(self) -> str
    Создает и формулирует запрос к модели OpenAI для генерации описания
    натальной карты на основе предварительно рассчитанных астрологических
    данных.
    """

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

    def __init__(self, birth_date: datetime, birth_place: str) -> None:
        """
        Инициализация экземпляра класса GetNatalChart.

        Использует дату и место рождения для создания натальной карты с
        помощью расчетов астрологических данных.

        Параметры:
            birth_date (datetime): Дата и время рождения.
            birth_place (str): Место рождения в текстовом формате.
        """
        super().__init__()
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)

    def user_request(self) -> str:
        """
        Формирует запрос к модели OpenAI для интерпретации астрологических
        данных и создания текста натальной карты.

        Основываясь на рассчитанных положениях планет и астрологических домов,
        генерирует запрос,
        содержащий основную информацию для создания детального и
        персонализированного анализа натальной карты.

        Возвращает:
            Строка запроса, которая включает дату рождения, место рождения,
            положения планет и астрологические дома,
            предоставляя все необходимые данные для генерации текста натальной
            карты.
        """
        res = ("интерпретируй эти данные и предоставить информацию"
               " о влиянии этих планет и домов на  натальную карту. "
               f"дата рождения {self.birth_date}. "
               f"Место рождения {self.birth_place}. "
               f"Планеты: {self.astralData.find_zodiac_sign()}, "
               f"позиции домов {self.astralData.calc_houses_positions()}.")
        return res


class GetSpecialHoroscope(BaseHoroscope, GetJulianDate):
    """
    Класс GetSpecialHoroscope наследует функциональность от BaseHoroscope и
    GetJulianDate, предоставляя специализированные инструменты для создания
    гороскопов с учетом положения Луны, лунного дня и оппозиции знаков зодиака.

    Атрибуты
    zodiac_signs: Список названий знаков зодиака.
    zodiac_sign: Знак зодиака, для которого создается гороскоп.
    position_moon: Текущее положение Луны в зодиакальном круге.
    description: Описание для запроса в OpenAI,
    специфичное для данного типа гороскопа.

    Методы
    calc_position_moon(): Расчет текущего положения Луны.
    moon_in_sign(): Определение знака зодиака и астрологического дома Луны.
    opposite_zodiac_sign(): Вычисление противоположного знака зодиака и
    связанного с ним дома.
    get_lunar_day(): Расчет лунного дня.
    description(): Формирование описания запроса для API OpenAI.
    user_request(): Создание пользовательского запроса для генерации гороскопа.
    """

    zodiac_signs = [
            "Овен", "Телец", "Близнецы", "Рак",
            "Лев", "Дева", "Весы", "Скорпион",
            "Стрелец", "Козерог", "Водолей", "Рыбы"
        ]

    def __init__(self, date: datetime, zodiac_sign: str) -> None:
        """
        Инициализация класса для получения специального гороскопа.

        Параметры:
            date (datetime.datetime): Дата для расчета положения Луны и
            лунных дней.
            zodiac_sign (str): Знак зодиака для гороскопа.
        """
        BaseHoroscope.__init__(self)
        GetJulianDate.__init__(self, date)
        self.zodiac_sign = zodiac_sign
        self.position_moon = self.calc_position_moon()
        self.description = self.description()

    def calc_position_moon(self) -> str:
        """
        Расчет текущего положения Луны в зодиакальном круге.

        Возвращает:
            Положение Луны в градусах зодиакального круга.
        """
        position_moon = swe.calc_ut(self.jd, swe.MOON)[0][0]
        return position_moon

    def moon_in_sign(self) -> tuple:
        """
        Определяет знак зодиака и астрологический дом для текущего положения
        Луны.

        Возвращает:
            Кортеж, содержащий знак зодиака и номер астрологического дома Луны.
        """
        houses = list(range(1, 13))
        index = int(self.position_moon // 30)
        return (self.zodiac_signs[index], houses[index])

    def opposite_zodiac_sign(self) -> tuple:
        """
        Определяет противоположный знак зодиака и астрологический дом
        относительно текущего положения Луны.

        Возвращает:
            Кортеж, содержащий противоположный знак зодиака и номер
            астрологического дома.
        """
        houses = list(range(1, 13))
        if self.position_moon >= 180:
            index = int((self.position_moon - 180) // 30)
        else:
            index = int((self.position_moon + 180) // 30)
        return (self.zodiac_signs[index], houses[index])

    def get_lunar_day(self) -> int:
        """
        Расчет текущего лунного дня на основе даты.

        Возвращает:
            Номер лунного дня.
        """
        # Получаем следующее и предыдущее новолуние относительно указанной даты
        prev_moon = ephem.previous_new_moon(self.date)

        # Рассчитываем лунный день
        lunar_day = self.date.day - prev_moon.datetime().day + 1

        return lunar_day

    def description(self) -> str:
        """
        Описание задачи для генерации специального гороскопа моделью OpenAI.

        Возвращает:
            Строка с описанием задачи.
        """
        des = ('Ты профессиональный астролог, сейчас ты мне делаешь '
               'предсказание, начни повествование с фразы "в этот день" '
               'Знак зодиака, в котором находится луна, указывает на '
               'положительные аспекты, а знак зодиака противоположный лунному.'
               ' указывает на отрицательные аспекты.'
               'Предсказание должно быть не менее 800 символов.'
               'В конце добавь влияние лунного дня.')
        return des

    def user_request(self) -> str:
        """
        Создает специфический запрос пользователя для генерации гороскопа.

        Возвращает:
            Строка запроса пользователя.
        """
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

# astralData = GetAstralData(datetime(1988, 6, 15, 17, 45), 'Смоленск')
# print(astralData.calc_planet_position(swe.MERCURY))
# print(astralData.calc_planet_positions())
# print(astralData.find_zodiac_sign())
# print(astralData.calc_houses_positions())
