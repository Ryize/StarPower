"""
Модуль бизнес-логики приложения Flask для прогнозирования гороскопов.

Этот модуль отвечает за обработку загружаемых файлов, определение дат для
различных периодов гороскопа(сегодня, неделя, месяц, год) и удаление ненужных
файлов после использования. Включает в себя функции для проверки допустимости
типов файлов, расчёта даты для прогноза и удаления файлов.

Функции:
    allowed_file(filename: str) -> bool:
        Проверяет, допустимо ли расширение файла для загрузки, основываясь на наборе
        разрешенных типов файлов.

    date_horoscope(period: str) -> str:
        Возвращает строковое представление начальной даты для заданного периода прогноза
        гороскопа.

    delete_file(file_path: str) -> None:
        Удаляет файл по заданному пути. Используется для очистки временных
        или не нужных более файлов.

Константы:
    Использует ALLOWED_EXTENSIONS из модуля app для определения допустимых типов файлов.

Зависимости:
    Для корректной работы функций этого модуля необходимы:
    - Константа ALLOWED_EXTENSIONS, определенная в модуле app.
    - Модули os и datetime для работы с файловой системой и датами соответственно.
"""
import os
from datetime import datetime, timedelta

from app import ALLOWED_EXTENSIONS


def allowed_file(filename: str) -> bool:
    """
    Функция проверки допустимости расширения файла для загрузки.
    Параметры:
        filename (str): Имя файла, включая его расширение, для проверки на допустимость.

    Возвращает:
        bool: Возвращает True, если расширение файла находится в списке допустимых
        расширений, иначе False.

    Пример:
        >>> allowed_file("example.jpg")
        True
        >>> allowed_file("example.sadkcfa")
        False

    Зависимости:
        Для работы функции необходим доступ к константе ALLOWED_EXTENSIONS,
        хранящейся в модуле, отвечающем за глобальные настройки
        приложения (например, app.py).
    """
    filename_split = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and filename_split in ALLOWED_EXTENSIONS


def date_horoscope(period: str) -> str:
    """
    Определяет начальную дату для заданного периода гороскопа.

    Параметры:
        period (str): Период времени для определения начальной даты. Допустимые значения:
        'today', 'week', 'month', 'year'.

    Возвращает:
        str: Строковое представление начальной даты заданного периода
         в формате 'YYYY-MM-DD'.

    Примеры использования:
        >>> date_horoscope("today")
        '2023-04-01'
        >>> date_horoscope("week")
        '2023-03-27'
        >>> date_horoscope("month")
        '2023-04-01'
        >>> date_horoscope("year")
        '2023-01-01'

    Зависимости:
        Для работы функции требуется импортирование модуля datetime для получения
        текущей даты и работы с датами.
    """
    today = datetime.now()

    if period == 'today':
        date = today.strftime('%Y-%m-%d')
    elif period == 'week':
        date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    elif period == 'month':
        date = today.strftime('%Y-%m-01')
    elif period == 'year':
        date = today.strftime('%Y-01-01')

    return date


def delete_file(file_path: str) -> None:
    """
    Удаляет файл по заданному пути, если файл существует.

    Параметры:
        file_path (str): Полный путь к файлу, который нужно удалить.

    Возвращает:
        None: Функция не возвращает значение.

    Пример использования:
        >>> delete_file("/path/to/unneeded/file.txt")
        Файл "/path/to/unneeded/file.txt" удален, если он существовал.

    Зависимости:
        Для работы функции требуется импортирование модуля os для доступа к
        файловой системе и выполнения операций удаления.
    """
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
