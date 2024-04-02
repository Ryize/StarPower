from horoscope_logic import BaseHoroscope, GetAstralData
from datetime import datetime
from copy import copy
import calendar
import time


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
        self.len_month = calendar.monthrange(self.c_year, self.c_month)[1]

    def tranzit(self):
        count = 0
        res = ''
        # положение натальных планет
        position_planets = self.astralData.calc_planet_positions()
        for natal_planet in self.personal_planets:
            for day in range(1, self.len_month + 1):
                day_month = datetime(self.c_year, self.c_month, day, 12, 0)
                dayAstralData = GetAstralData(day_month, self.c_place)
                # позиция планет на данный день
                day_position_planets = dayAstralData.calc_planet_positions()
                del day_position_planets['Луна']
                for day_planet in day_position_planets:
                    aspect = TranzitMonth.calculate_aspect(
                        position_planets[natal_planet],
                        day_position_planets[day_planet],
                        0.3)
                    if aspect:
                        count += 1
                        res += (f'Натальная планета {natal_planet} находится в'
                                f' аспекте {aspect} с транзитной планетой '
                                f'{day_planet}\n')
        return res, count

    @staticmethod
    def calculate_aspect(degree1, degree2, orbis):
        difference = abs(degree1 - degree2) % 360
        if difference > 180:
            difference = 360 - difference

        if difference <= orbis:  # Погрешность 0 градусов для учёта орбиса
            return 'соединение'
        elif abs(difference - 60) <= orbis:
            return 'секстиль'
        elif abs(difference - 90) <= orbis:
            return 'квадрат'
        elif abs(difference - 120) <= orbis:
            return 'тригон'
        elif abs(difference - 180) <= orbis:
            return 'оппозиция'

    # def aspect(self, position_planets, basic_planet):
    #     result = ''
    #     position_planets = copy(position_planets)
    #     main_planet = position_planets.pop(basic_planet)
    #     for planet in position_planets:
    #         res = GetNatalChart2.calculate_aspect(main_planet,
    #                                               position_planets[planet])
    #         if res:
    #             result += (f'У планет {basic_planet} и {planet}'
    #                        f' аспект {res}.\n')
    #     return result

    # def user_request(self, planet, aspects):
    #     res = (f'{self.astralData.find_zodiac_sign()[planet]}'
    #            f'{aspects}')
    #     return res

    # def get_response(self, planet, aspects):
    #     completion = self.client.chat.completions.create(
    #         model="gpt-3.5-turbo-1106",
    #         messages=[
    #             {"role": "system", "content": self.description},
    #             {"role": "user", "content": self.user_request(planet,
    #                                                           aspects)}
    #         ]
    #         )
    #     return completion.choices[0].message.content

    # def natal_chart(self):

    #     result = ''
    #     position_planets = self.astralData.calc_planet_positions()
    #     for planet in self.personal_planets:
    #         aspects = self.aspect(position_planets, planet)
    #         result += f'<h2>{planet}</h2><br>'
    #         result += f'{self.get_response(planet, aspects)}<br><br>'
    #     return result


# get = GetNatalChart2(datetime(1988, 1, 29, 17, 45), 'Смоленск')
# print(get.natal_chart())
start_time = time.time()
get = TranzitMonth(datetime(1988, 1, 29, 17, 45), 'Смоленск')
elapsed_time = time.time() - start_time
print(get.tranzit())
print(elapsed_time)
