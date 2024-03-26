from horoscope_logic import BaseHoroscope, GetAstralData


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
