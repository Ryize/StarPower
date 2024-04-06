import calendar
from copy import copy
from datetime import datetime, timedelta

import swisseph as swe

from horoscope_logic import BaseHoroscope, GetAstralData


class GetNatalChart2(BaseHoroscope):
    """
    Этот класс предназначен для детального анализа влияния планет на
    психологический портрет человека. Описание включает в себя функции планет
    в знаках зодиака и их аспекты, что позволяет сделать выводы о личностных
    качествах и предрасположенностях.

    Атрибуты
    personal_planets: Список личных планет, влияние которых анализируется.
    description: Текстовое описание задания для модели OpenAI.
    Методы
    __init__(self, birth_date: datetime, birth_place: str) -> None
    Инициализирует экземпляр класса, устанавливая дату рождения, место
    рождения и создает объект GetAstralData для расчета астрологических данных.

    calculate_aspect(degree1: float, degree2: float) -> str
    Расчет аспекта между двумя планетами. Определяет тип аспекта на основе
    разницы градусов между планетами.

    aspect(self, position_planets: dict, basic_planet: str) -> str
    Анализирует аспекты между выбранной планетой и остальными планетами.
    Возвращает текстовое описание аспектов.

    user_request(self, planet: str, aspects: str) -> str
    Формирует запрос пользователя для генерации анализа влияния планеты и ее
    аспектов на личность.

    get_response(self, planet: str, aspects: str) -> str
    Отправляет запрос в OpenAI и возвращает сгенерированный текст анализа
    планеты и ее аспектов.

    natal_chart(self) -> str
    Генерирует полный анализ натальной карты, анализируя влияние личных планет
    и их аспектов. Возвращает текстовое представление анализа.
        """

    personal_planets = ['Солнце',
                        'Луна',
                        'Меркурий',
                        'Венера',
                        'Марс'
                        ]

    description = (
        'Ты профессиональный астролог. Сейчас ты мне рассказываешь как данная '
        'планета влияет на меня. В начале опиши что значит эта планета в знаке'
        ' зодиака, потом распиши ее аспекты. Планета в знаке задика несет'
        ' определенную функцию, а аспекты помогают или мешают - сделай из'
        ' этого вывод как планета будет влиять на мой психологический портрет.'
        ' Проверь текст, он должен быть только на русском языке.'
        )

    def __init__(self, birth_date: datetime, birth_place: str) -> None:
        """
        Инициализирует новый экземпляр класса, сохраняя дату и место рождения,
        а также создавая экземпляр класса GetAstralData для последующих
        астрологических вычислений.

        Параметры:
        birth_date: Дата рождения индивида, используется для расчёта
        астрологических позиций.
        birth_place: Место рождения индивида, необходимо для точных
        астрологических расчётов.
        """
        super().__init__()
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)

    @staticmethod
    def calculate_aspect(degree1: float, degree2: float, orbis: float) -> str:
        """
        Статический метод для расчета аспектов между двумя планетами с учетом
        орбиса.

        Параметры:
        degree1: Градусное положение первой планеты.
        degree2: Градусное положение второй планеты.
        orbis: Погрешность для учета орбиса.
        Возвращает:
        Название аспекта между двумя планетами, если таковой имеется.
        """
        difference = abs(degree1 - degree2) % 360
        if difference > 180:
            difference = 360 - difference

        if difference <= orbis:  # Погрешность для учёта орбиса
            return 'соединение'
        elif abs(difference - 60) <= orbis:
            return 'секстиль'
        elif abs(difference - 90) <= orbis:
            return 'квадрат'
        elif abs(difference - 120) <= orbis:
            return 'тригон'
        elif abs(difference - 180) <= orbis:
            return 'оппозиция'

    def aspect(self, position_planets: dict, basic_planet: float) -> str:
        """
        Определяет астрологические аспекты между выбранной планетой и другими
        планетами.

        Параметры:
        position_planets: Словарь, содержащий позиции планет.
        basic_planet: Основная планета для анализа аспектов.
        Возвращает:
        Строку, содержащую информацию об астрологических аспектах между
        основной
        планетой и остальными планетами в словаре.
        """
        result = ''
        position_planets = copy(position_planets)
        main_planet = position_planets.pop(basic_planet)
        for planet in position_planets:
            res = GetNatalChart2.calculate_aspect(main_planet,
                                                  position_planets[planet],
                                                  orbis=8)
            if res:
                result += (f'У планет {basic_planet} и {planet}'
                           f' аспект {res}.\n')
        return result

    def user_request(self, planet: str, aspects: str) -> str:
        """
        Создаёт запрос пользователя, основанный на знаке Зодиака планеты и её
        аспектах.

        Параметры:
        planet: Планета, для которой выполняется запрос.
        aspects: Строка, содержащая аспекты планеты.
        Возвращает:
        Строку запроса пользователя.
        """
        res = (f'{self.astralData.find_zodiac_sign()[planet]}'
               f'{aspects}')
        return res

    def get_response(self, planet: str, aspects: str) -> str:
        """
        Получает ответ на запрос пользователя, используя предоставленные
        астрологические данные.

        Параметры:
        planet: Планета, для которой запрашивается ответ.
        aspects: Аспекты планеты.
        Возвращает:
        Строку с ответом на запрос.
        """
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request(planet,
                                                              aspects)}
            ]
            )
        return completion.choices[0].message.content

    def natal_chart(self) -> str:
        """
        Создаёт натальную карту, анализируя позиции планет и их аспекты.

        Возвращает:
        Строку, содержащую HTML-форматированную натальную карту с анализом
        аспектов для каждой планеты.
        """
        result = ''
        position_planets = self.astralData.calc_planet_positions()
        for planet in self.personal_planets:
            aspects = self.aspect(position_planets, planet)
            result += f'<h2>{planet}</h2><br>'
            result += f'{self.get_response(planet, aspects)}<br><br>'
        return result


class TranzitMonth(BaseHoroscope, GetNatalChart2):
    """
    Прогнозы создаются путем анализа влияния транзитных планет на натальную
    карту человека. Класс учитывает временные рамки действия каждого
    аспекта и предоставляет рекомендации на месяц.

    Методы
    tranzit(self) -> str
    Анализирует транзиты планет за месяц и их влияние на натальные планеты.
    Возвращает текстовое описание прогноза.

    calculate_aspect(degree1: float, degree2: float, orbis: float) -> str
    Расчет аспекта между натальной и транзитной планетами с учетом орбиса.

    user_request(self) -> str
    Формирует запрос пользователя для генерации месячного прогноза.

    user_request_con(self) -> str
    Дополнительная функция для формирования запроса, связанного с
    консультацией.

    get_response_con(self) -> str
    Отправляет запрос в OpenAI для получения консультационного прогноза на
    месяц.
        """

    personal_planets = ['Солнце',
                        'Луна',
                        'Меркурий',
                        'Венера',
                        'Марс'
                        ]

    # Влияние аспекта персональных планет
    aspect_ratio_p = 2

    # Влияние аспекта социальных планет
    aspect_ratio_s = 7
    tranzit_planets = [('Солнце', aspect_ratio_p),
                       ('Меркурий', aspect_ratio_p),
                       ('Венера', aspect_ratio_p),
                       ('Марс', aspect_ratio_p),
                       ('Юпитер', aspect_ratio_s),
                       ('Сатурн', aspect_ratio_s)
                       ]

    description_con = (
        'На основе полученной информации составь астрологический прогноз на '
        'месяц. Опиши начало месяца, середину и конец. Как лучше провести '
        'каждое время чем лучше заниматься, чего опасаться, какие силы будут '
        'действовать, какие будут чувства и эмоции. При описании периодов не '
        'используй числа. Тебе нужно выстроить доверительную связь с клиентов '
        'во время сеанса астрологии, быть чутким и проявлять эмпатию.'
        )

    description = (
        'Ты профессиональный астролог. Сейчас идет сеанс предсказания '
        'на основе транзитнов на месяц. Проанализируй влияние каждого аспекта,'
        'какое время он будет действовать, как это повлияет на меня, что мне '
        'сделать что бы провести это время максимально продуктивно. Чего стоит'
        ' опасаться или наоборот что сможет порадовать. '
        'Если какой то аспект действует в течении нескольких дней'
        ' подряд обьедени их в один период как один аспект.'
        'С учетом полученной информации сделай подробное описание месяца.'
        'Проверь текст, он должен быть только на русском языке. '
        'После каждого пункта для разделения пропускай строку'
        )

    def __init__(self, birth_date, birth_place) -> None:
        super().__init__()

        # Текущий месяц и год
        self.c_month = datetime.now().month
        self.c_year = datetime.now().year
        # Текущее место
        self.c_place = birth_place
        # Дата рождения
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)
        self.len_month = calendar.monthrange(self.c_year, self.c_month)[1]

    def tranzit(self) -> str:
        """
        Анализирует транзиты планет на каждый день текущего месяца
        относительно натальной карты.

        Возвращает:
        Строку с описанием значимых транзитов планет для каждого дня текущего
        месяца.
        """
        res = ''
        # положение натальных планет
        position_planets = self.astralData.calc_planet_positions()
        for day in range(1, self.len_month + 1):
            day_month = datetime(self.c_year, self.c_month, day, 12, 0)
            dayAstralData = GetAstralData(day_month, self.c_place)
            # позиция планет на данный день
            day_position_planets = dayAstralData.calc_planet_positions()
            for natal_planet in self.personal_planets:
                for day_planet in self.tranzit_planets:
                    aspect = TranzitMonth.calculate_aspect(
                        position_planets[natal_planet],
                        day_position_planets[day_planet[0]],
                        0.3)
                    if aspect:
                        res += (f'{natal_planet} находится в'
                                f' аспекте {aspect} с'
                                f'{day_planet[0]}, наибольшее влияние аспекта '
                                f'с {max(1, day - day_planet[1])} числа по'
                                f'{min(self.len_month, day + day_planet[1])}')
        return res

    def user_request(self) -> str:
        """
        Формирует пользовательский запрос, содержащий информацию о транзитах
        планет за текущий месяц.

        Возвращает:
        Строку с запросом пользователя.
        """
        res = f'{self.tranzit()}'
        return res

    def user_request_con(self) -> str:
        """
        Формирует пользовательский запрос.

        Возвращает:
        Строку с запросом пользователя.
        """
        res = f'{self.get_response()}'
        return res

    def get_response_con(self) -> str:
        """
        Получает ответ на запрос пользователя от API GPT-3.5.

        Возвращает:
        Строку с ответом API на запрос пользователя.
        """
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description_con},
                {"role": "user", "content": self.user_request_con()}
            ]
            )
        return completion.choices[0].message.content


class TranzitYear(BaseHoroscope):
    """
    В разработке.
    """

    personal_planets = ['Солнце',
                        'Луна',
                        'Меркурий',
                        'Венера',
                        'Марс'
                        ]

    # Влияние аспекта персональных планет
    aspect_ratio_p = 2

    # Влияние аспекта социальных планет
    aspect_ratio_s = 7
    tranzit_planets = ['Уран',
                       'Нептун',
                       'Плутон'
                       ]

    description_con = (
        ''
        )

    description = (
        ''
        )

    def __init__(self, birth_date, birth_place) -> None:
        super().__init__()

        # Текущий месяц и год
        self.c_month = datetime.now().month
        self.c_year = datetime.now().year
        # Текущее место
        self.c_place = birth_place
        # Дата рождения
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)
        self.len_year = lambda year: 366 if calendar.isleap(
            self.c_year) else 365

    def tranzit(self):
        res = ''
        # положение натальных планет
        position_planets = self.astralData.calc_planet_positions()

        for day in range(1, self.len_year(self.c_year) + 1):
            day_year = self.day_of_year_to_date(self.c_year, day)
            dayAstralData = GetAstralData(day_year, self.c_place)
            # позиция планет на данный день
            day_position_planet = dayAstralData.calc_planet_position(
                swe.URANUS)
            for natal_planet in self.personal_planets:
                aspect = TranzitYear.calculate_aspect(
                    position_planets[natal_planet],
                    day_position_planet,
                    0.3)
                if aspect:
                    res += (f'{natal_planet} находится в'
                            f' аспекте {aspect} с '
                            f'Ураном, {day_year}'
                            )

        return res

    def day_of_year_to_date(self, year, day_of_year):
        start_of_year = datetime(year, 1, 1)
        delta = timedelta(days=day_of_year - 1)
        target_date = start_of_year + delta
        return target_date

    @staticmethod
    def calculate_aspect(degree1, degree2, orbis):
        difference = abs(degree1 - degree2) % 360
        if difference > 180:
            difference = 360 - difference

        if difference <= orbis:  # Погрешность для учёта орбиса
            return 'соединение'
        elif abs(difference - 60) <= orbis:
            return 'секстиль'
        elif abs(difference - 90) <= orbis:
            return 'квадрат'
        elif abs(difference - 120) <= orbis:
            return 'тригон'
        elif abs(difference - 180) <= orbis:
            return 'оппозиция'

    def user_request(self):
        res = f'{self.tranzit()}'
        return res

    def user_request_con(self):
        res = f'Здравствуйте меня зовут Владимир, {self.get_response()}'
        return res

    def get_response_con(self):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description_con},
                {"role": "user", "content": self.user_request_con()}
            ]
            )
        return completion.choices[0].message.content

# get = GetNatalChart2(datetime(1988, 1, 29, 17, 45), 'Смоленск')
# print(get.natal_chart())


# get = TranzitYear(datetime(2001, 1, 29, 17, 45), 'Смоленск')

# print(get.tranzit())
