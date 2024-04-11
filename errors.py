
from flask import render_template

from app import app


@app.errorhandler(404)
def error404(status) -> str:
    """
    Функция обрабатывает ошибку HTTP 404.
    :param status: int(Код ошибки)
    :return: 404.html (Шаблон страницы ошибки)
    """
    return render_template("errors/404.html")


@app.errorhandler(500)
def error500(status) -> str:
    """
    Функция обрабатывает ошибку HTTP 500.
    :param status: int(Код ошибки)
    :return: 500.html (Шаблон страницы ошибки)
    """
    return render_template("errors/500.html")