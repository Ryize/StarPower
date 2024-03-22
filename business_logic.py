import os

from datetime import datetime, timedelta

from app import ALLOWED_EXTENSIONS


def allowed_file(filename: str) -> bool:
    """
    Проверяет расширение загружаемого файла и сравнивает его со списком
    допустимых расширений, которые хранятся в константе ALLOWED_EXTENSIONS.

    :param filename: имя файла
    :type filename: str
    :return: результат проверки
    :rtype: bool
    """
    filename_split = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and filename_split in ALLOWED_EXTENSIONS


def date_horoscope(period):

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


def delete_file(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
