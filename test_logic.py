from openai import OpenAI
client = OpenAI()

day = ''

description = (
    'Ты профессиональный астролог. Будь уверенен в своих предсказаниях, '
    'они не должны содержать гендерных различий. '
    'Давай четкие и полезные советы. '
    'Текст предсказания должен быть грамотно написан, '
    'с учетом особенностей русского языка. '
    'Данные для предсказаний бери с лучших сайтов по астрологии в интернете.'
)

user_data = {
    'zodiac_sign': 'водолей',
    'data': 'в этом году'
}

period = {
    'year': ['в этом году', '2000 - 2500'],
    'month': ['в этом месяце', '1000 - 1500'],
    'week': ['на этой неделе', '1000 - 1500'],
    'today': ['сегодня', '500 - 700'],
    'day_of_the_week': [f'{day}', '500-700']
}

user_request = f"Я {user_data['zodiac_sign']}, что меня ждет {period['year'][0]}? Предсказание должно содержать 2000 символов. В начале опиши начало года, потом что будет в середине и далее чем год закончится"

print(user_request)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": description},
    {"role": "user", "content": f"Я {user_data['zodiac_sign']}, что меня ждет {period['year'][0]}? Предсказание должно содержать 2000 символов. В начале опиши начало года, потом что будет в середине и далее чем год закончится"}
  ]
)

print(f'{completion.usage.prompt_tokens} prompt tokens used.')
print(completion.choices[0].message.content)


class GetHoroscope:

    add_inf_year = ('В начале опиши начало года, потом что будет в середине'
                    'и далее чем год закончится.')

    add_inf_month = ('В начале опиши начало месяца, потом что будет в середине'
                     'и далее чем месяц закончится.')
    add_inf_week = ('В начале опиши начале недели, потом что будет в середине'
                    'и далее чем неделя закончится.')

    description_period = {
        'year': ['в этом году', '2000 - 2500', add_inf_year],
        'month': ['в этом месяце', '1000 - 1500', add_inf_month],
        'week': ['на этой неделе', '1000 - 1500', add_inf_week],
        'today': ['сегодня', '500 - 700'],
        'day_of_the_week': [f'{day}', '500-700']
    }

    def __init__(self, zodiac_sign, period, day=None) -> None:
        self.zodiac_sign = zodiac_sign
        self.period = period
        self.day = day
