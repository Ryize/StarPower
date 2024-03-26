from horoscope_logic import BaseHoroscope, GetAstralData
from datetime import datetime
from copy import copy


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
            result += f'{self.get_response(planet, aspects)}\n\n'
        return result


get = GetNatalChart2(datetime(1988, 1, 29, 17, 45), 'Смоленск')
print(get.natal_chart())
