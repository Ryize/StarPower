from openai import OpenAI
import os
from dotenv import load_dotenv


class GetHoroscope:
    client = None

    day = None

    add_inf_year = ('Данные возьми с сайта по астрологии.'
                    'Пожалуйста, включи описание общих тенденций, '
                    'возможностей и предостережений.'
                    'Не упоминай какой сейчас год.'
                    )

    add_inf_month = ('Данные возьми с сайта по астрологии.'
                     'Опиши начало месяца, потом что будет в середине'
                     'и далее чем месяц закончится.')
    add_inf_week = ('Данные возьми с сайта по астрологии.'
                    'Опиши начало недели, потом что будет в середине'
                    'и далее чем неделя закончится.')
    add_inf_day = 'Данные возьми с сайта по астрологии.'
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
        'day_of_the_week': [f'{day}', '500-700', add_inf_day_of_the_week]
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
        res = (f"Я {self.zodiac_sign}, что меня ждет "
               f"{self.des_period[self.period][0]}? Предсказание должно "
               f"содержать {self.des_period[self.period][1]} символов. "
               f"{self.des_period[self.period][2]}")
        print(res)
        return res


horoscope = GetHoroscope('Скорпион', 'today')
print(horoscope.get_response())
