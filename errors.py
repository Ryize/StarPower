
from app import app
from flask import redirect, render_template, flash, url_for, Response


@app.errorhandler(404)
def error404(status) -> Response:
    """
    Функция обрабатывает ошибку HTTP 401, перенаправляя пользователя на страницу авторизации.
    :param status: Int(Код ошибки)
    :return: None
    """
    flash(
        {"title": "Внимание!", "message": "Необходимо авторизоваться."}, category="info"
    )
    return redirect(url_for("input_user")), 301