import re

from flask import flash
from models import User
def check_new_user(login: str, email: str, password: str) -> bool:
    """
    Проверяет данные нового пользователя перед регистрацией.

    pattern_login - Эта регулярка проверяет,
    соответствует ли строка следующим условиям:
    Длина строки от 5 до 25 символов.
    Строка может содержать только латинские буквы в верхнем и нижнем регистре,
    цифры, а также символы !, ?,.
    Строка не должна содержать пробелы или другие специальные символы.

    pattern_email - Она проверяет наличие символа '@' в строке
    и наличие хотя бы одного символа до и после символа '@'.
    Допустимыми символами являются буквы, цифры, дефисы и точки.
    За символом '@' должна следовать доменная часть email-адреса,
    состоящая из букв, цифр, дефисов и точек, где точка не может быть первым
    или последним символом, и между точками должен быть хотя бы один символ.
    В конце доменной части должен быть указан домен верхнего уровня
    из двух-четырех символов, например '.com' или '.ru'.

    pattern_password - Проверяет, что строка содержит от 5 до 36 символов,
    состоящих из букв (в любом регистре), цифр и знаков !, ? или _.
    То есть, данное регулярное выражение подходит для проверки корректности
    пароля, который должен содержать только разрешенные символы и быть длиной
    не менее 5 и не более 36 символов.

    :param login: логин пользователя.
    :type login: str
    :param email: электронная почта пользователя.
    :type email: str
    :param password: пароль пользователя.
    :type password: str
    :return: результат проверки.
    :rtype: bool
    """
    pattern_login = r'^[a-zA-Z!?\d]{5,25}$'  # Регулярки объясняются в доке
    pattern_email = r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$'
    pattern_password = r'^[a-zA-Z!?\d]{5,36}$'
    if User.query.filter_by(login=login).first():
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Такой пользователь уже существует',
            },
            category='error',
        )
        return False
    elif User.query.filter_by(email=email).first():
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Пользователь с таким E-mail уже есть',
            },
            category='error',
        )
        return False
    elif re.match(pattern_login, login) is None:
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Логин должен состоять из 5-25 латинских букв, '
                           'цифр и символов!',
            },
            category='error',
        )
        return False
    elif re.match(pattern_email, email) is None:
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Вы ввели неверный формат почты!',
            },
            category='error',
        )
        return False
    elif re.match(pattern_password, password) is None:
        flash(
            {
                'title': 'Ошибка!',
                'message': 'Пароль должен состоять из 5-36 латинских букв, '
                           'цифр и символов',
            },
            category='error',
        )
        return False
    flash(
        {
            'title': 'Успешно!',
            'message': 'Вы успешно зарегистрированы, зайдите в кабинет',
        },
        category='success',
    )
    return True


class GetHoroscope:

    day = None

    add_inf_year = ('В начале опиши начало года, потом что будет в середине'
                    'и далее чем год закончится.')

    add_inf_month = ''
    add_inf_week = ''

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
