from horoscope_logic import BaseHoroscope, GetAstralData
from flask_login import current_user
from datetime import datetime


class GetNatalChart2(BaseHoroscope):

    description = (
        'Ты профессиональный астролог. Сейчас ты составляешь мою натальную'
        ' карту для этого я тебе передам данные о том какие планеты в момент'
        ' моего рождения находились в каких знаках зодиака. Максимально'
        ' подробно опиши влияние планет в знаках зодиака на меня, описание'
        ' каждой планеты должно содержать не менее 5 предложений. Составь мой'
        ' психологический портрет, выдели мои слабые и сильные стороны.'
        ' Подскажи к чему стремиться и в чем развиваться.'
        )

    def __init__(self, birth_date, birth_place) -> None:
        super().__init__()
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.astralData = GetAstralData(self.birth_date, self.birth_place)

    def user_request(self):
        res = (f'Привет, меня зовут Елена, '
               f'вот мои данные {self.astralData.find_zodiac_sign()}')
        return res


get = GetNatalChart2(datetime(1988, 1, 29, 17, 45), 'Смоленск')
print(get.get_response())
