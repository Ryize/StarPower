from horoscope_logic import BaseHoroscope, GetAstralData
from datetime import datetime, timedelta
from copy import copy
import calendar
import swisseph as swe


class GetNatalChart2(BaseHoroscope):

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

    def __init__(self, birth_date, birth_place) -> None:
        super().__init__()
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)

    @staticmethod
    def calculate_aspect(degree1, degree2):

        difference = abs(degree1 - degree2) % 360
        if difference > 180:
            difference = 360 - difference

        if difference < 8:  # Погрешность +-8 градусов для учёта орбиса
            return 'соединение'
        elif abs(difference - 60) < 8:
            return 'секстиль'
        elif abs(difference - 90) < 8:
            return 'квадрат'
        elif abs(difference - 120) < 8:
            return 'тригон'
        elif abs(difference - 180) < 8:
            return 'оппозиция'

    def aspect(self, position_planets, basic_planet):
        result = ''
        position_planets = copy(position_planets)
        main_planet = position_planets.pop(basic_planet)
        for planet in position_planets:
            res = GetNatalChart2.calculate_aspect(main_planet,
                                                  position_planets[planet])
            if res:
                result += (f'У планет {basic_planet} и {planet}'
                           f' аспект {res}.\n')
        return result

    def user_request(self, planet, aspects):
        res = (f'{self.astralData.find_zodiac_sign()[planet]}'
               f'{aspects}')
        return res

    def get_response(self, planet, aspects):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request(planet,
                                                              aspects)}
            ]
            )
        return completion.choices[0].message.content

    def natal_chart(self):

        result = ''
        position_planets = self.astralData.calc_planet_positions()
        for planet in self.personal_planets:
            aspects = self.aspect(position_planets, planet)
            result += f'<h2>{planet}</h2><br>'
            result += f'{self.get_response(planet, aspects)}<br><br>'
        return result


class TranzitMonth(BaseHoroscope):

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

    def tranzit(self):
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
        res = f'{self.get_response()}'
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


class TranzitYear(BaseHoroscope):

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


get = TranzitYear(datetime(2001, 1, 29, 17, 45), 'Смоленск')

print(get.tranzit())
