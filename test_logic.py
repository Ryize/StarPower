from openai import OpenAI
import os
from dotenv import load_dotenv


class GetHoroscope:
    client = None

    day = None

    add_inf_year = ('В начале опиши начало года, потом что будет в середине'
                    'и далее чем год закончится.')

    add_inf_month = ('В начале опиши начало месяца, потом что будет в середине'
                     'и далее чем месяц закончится.')
    add_inf_week = ('В начале опиши начале недели, потом что будет в середине'
                    'и далее чем неделя закончится.')

    description = (
        'Ты профессиональный астролог. Будь уверенен в своих предсказаниях, '
        'они не должны содержать гендерных различий. '
        'Давай четкие и полезные советы. '
        'Текст предсказания должен быть грамотно написан, '
        'с учетом особенностей русского языка. '
        'Данные для предсказаний бери с лучших сайтов по астрологии.'
    )

    des_period = {
        'year': ['в этом году', '2000 - 2500', add_inf_year],
        'month': ['в этом месяце', '1000 - 1500', add_inf_month],
        'week': ['на этой неделе', '1000 - 1500', add_inf_week],
        'today': ['сегодня', '500 - 700'],
        'day_of_the_week': [f'{day}', '500-700']
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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request()}
            ]
            )
        return completion.choices[0].message.content

    def user_request(self):
        res = f"Я {self.zodiac_sign}, что меня ждет {self.des_period[self.period][0]}? Предсказание должно содержать {self.des_period[self.period][1]} символов."
        return res


horoscope = GetHoroscope('Водолей', 'year')
print(horoscope.get_response())
